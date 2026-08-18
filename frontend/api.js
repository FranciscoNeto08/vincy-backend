const Api = (function () {

    const BASE_URL = "https://vincy-backend-u43m.onrender.com";

    const pending = new Map();
    const getCache = new Map();

    const GET_CACHE_MS = 600;
    const REQUEST_TIMEOUT_MS = 65000;
    const RETRY_DELAY_MS = 1500;
    const MAX_RETRIES = 1;


    function requestKey(method, path, body){
        return `${method}:${path}:${body === undefined ? "" : JSON.stringify(body)}`;
    }


    function clearGetCache(){
        getCache.clear();
    }


    function esperar(ms){
        return new Promise(resolve => setTimeout(resolve, ms));
    }


    function erroDeRedeOuTimeout(err){
        if(!err) return false;

        return (
            err.name === "AbortError" ||
            err instanceof TypeError
        );
    }


    async function fetchComTimeout(
        url,
        options = {},
        timeout = REQUEST_TIMEOUT_MS
    ){

        const controller = new AbortController();

        const timeoutId = setTimeout(()=>{
            controller.abort();
        }, timeout);

        try{

            return await fetch(url, {
                ...options,
                signal: controller.signal
            });

        }finally{

            clearTimeout(timeoutId);
        }
    }


    async function executeFetch(
        path,
        {
            method = "GET",
            body,
            auth = true,
            headers = {},
            timeout = REQUEST_TIMEOUT_MS,
            retry = true
        } = {}
    ){

        const upperMethod =
            String(method || "GET").toUpperCase();

        const finalHeaders = {
            "Content-Type": "application/json",
            ...headers
        };

        if(auth){

            const token = Auth.getToken();

            if(token){
                finalHeaders["Authorization"] =
                    `Bearer ${token}`;
            }
        }

        /*
          Retry automático apenas para GET.

          Para POST/PUT/PATCH/DELETE, repetir automaticamente
          pode duplicar operações caso o servidor tenha recebido
          a primeira requisição mas a resposta tenha se perdido.
        */
        const retriesPermitidos =
            retry && upperMethod === "GET"
                ? MAX_RETRIES
                : 0;

        let tentativa = 0;

        while(true){

            try{

                const response =
                    await fetchComTimeout(
                        BASE_URL + path,
                        {
                            method: upperMethod,
                            headers: finalHeaders,
                            body:
                                body !== undefined
                                    ? JSON.stringify(body)
                                    : undefined
                        },
                        timeout
                    );


                if(
                    response.status === 401 &&
                    auth
                ){

                    Auth.logout();

                    throw new Error(
                        "Sessão expirada. Faça login novamente."
                    );
                }


                if(response.status === 204){
                    return null;
                }


                const data =
                    await response
                        .json()
                        .catch(()=>null);


                if(!response.ok){

                    let message =
                        "Erro ao comunicar com o servidor.";

                    if(
                        data &&
                        typeof data.detail === "string"
                    ){

                        message = data.detail;

                    }
                    else if(
                        data &&
                        Array.isArray(data.detail)
                    ){

                        message =
                            data.detail
                                .map(item=>item.msg)
                                .join(", ");
                    }

                    throw new Error(message);
                }


                return data;

            }catch(err){

                const podeTentarNovamente =
                    tentativa < retriesPermitidos &&
                    erroDeRedeOuTimeout(err);

                if(podeTentarNovamente){

                    tentativa++;

                    console.warn(
                        `Servidor demorou para responder. Tentativa automática ${tentativa + 1}...`
                    );

                    await esperar(RETRY_DELAY_MS);

                    continue;
                }


                if(
                    err &&
                    err.name === "AbortError"
                ){

                    throw new Error(
                        "O servidor está iniciando. Aguarde alguns segundos e tente novamente."
                    );
                }


                if(err instanceof TypeError){

                    throw new Error(
                        "Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente."
                    );
                }


                throw err;
            }
        }
    }


    function request(
        path,
        {
            method = "GET",
            body,
            auth = true,
            headers = {},
            timeout,
            retry
        } = {}
    ){

        const upperMethod =
            String(method || "GET").toUpperCase();

        const key =
            requestKey(
                upperMethod,
                path,
                body
            );


        /*
          CACHE + REQUEST DEDUPLICATION PARA GET
        */
        if(upperMethod === "GET"){

            const cached =
                getCache.get(key);

            if(
                cached &&
                Date.now() - cached.timestamp
                    < GET_CACHE_MS
            ){

                return Promise.resolve(
                    cached.data
                );
            }


            if(pending.has(key)){
                return pending.get(key);
            }
        }


        /*
          Para mutações, dois cliques iguais
          reaproveitam a mesma Promise.
        */
        if(
            upperMethod !== "GET" &&
            pending.has(key)
        ){

            return pending.get(key);
        }


        const promise =
            executeFetch(
                path,
                {
                    method: upperMethod,
                    body,
                    auth,
                    headers,
                    timeout,
                    retry
                }
            )
            .then(data=>{

                if(upperMethod === "GET"){

                    getCache.set(
                        key,
                        {
                            data,
                            timestamp:
                                Date.now()
                        }
                    );

                }else{

                    clearGetCache();
                }

                return data;
            })
            .finally(()=>{

                pending.delete(key);
            });


        pending.set(
            key,
            promise
        );

        return promise;
    }


    async function login(
        email,
        password
    ){

        const key =
            `LOGIN:${String(email).toLowerCase()}`;

        /*
          Evita vários cliques no botão Entrar
          disparando vários logins.
        */
        if(pending.has(key)){
            return pending.get(key);
        }


        const promise =
            (async ()=>{

                const body =
                    new URLSearchParams();

                body.set(
                    "username",
                    email
                );

                body.set(
                    "password",
                    password
                );


                try{

                    const response =
                        await fetchComTimeout(
                            `${BASE_URL}/auth/login`,
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type":
                                        "application/x-www-form-urlencoded"
                                },
                                body
                            },
                            REQUEST_TIMEOUT_MS
                        );


                    const data =
                        await response
                            .json()
                            .catch(()=>null);


                    if(!response.ok){

                        const message =
                            (
                                data &&
                                data.detail
                            ) ||
                            "E-mail ou senha incorretos.";

                        throw new Error(
                            message
                        );
                    }


                    clearGetCache();

                    return data;

                }catch(err){

                    if(
                        err &&
                        err.name === "AbortError"
                    ){

                        throw new Error(
                            "O servidor está iniciando. Aguarde alguns segundos e tente novamente."
                        );
                    }


                    if(err instanceof TypeError){

                        throw new Error(
                            "Não foi possível conectar ao servidor. Tente novamente em alguns segundos."
                        );
                    }


                    throw err;
                }

            })()
            .finally(()=>{

                pending.delete(key);
            });


        pending.set(
            key,
            promise
        );

        return promise;
    }


    /*
      Acorda o backend discretamente.

      Chame isso assim que a tela de login carregar.
    */
    async function warmup(){

        const key = "WARMUP";

        if(pending.has(key)){
            return pending.get(key);
        }


        const promise =
            (async ()=>{

                try{

                    await executeFetch(
                        "/health",
                        {
                            method: "GET",
                            auth: false,
                            timeout: 65000,
                            retry: true
                        }
                    );

                    console.log(
                        "Backend pronto."
                    );

                    return true;

                }catch(err){

                    console.warn(
                        "Backend ainda está iniciando:",
                        err
                    );

                    return false;
                }

            })()
            .finally(()=>{

                pending.delete(key);
            });


        pending.set(
            key,
            promise
        );

        return promise;
    }


    return {

        BASE_URL,

        get:
            (path, opts)=>
                request(
                    path,
                    {
                        ...opts,
                        method: "GET"
                    }
                ),

        post:
            (path, body, opts)=>
                request(
                    path,
                    {
                        ...opts,
                        method: "POST",
                        body
                    }
                ),

        put:
            (path, body, opts)=>
                request(
                    path,
                    {
                        ...opts,
                        method: "PUT",
                        body
                    }
                ),

        patch:
            (path, body, opts)=>
                request(
                    path,
                    {
                        ...opts,
                        method: "PATCH",
                        body
                    }
                ),

        del:
            (path, opts)=>
                request(
                    path,
                    {
                        ...opts,
                        method: "DELETE"
                    }
                ),

        login,

        warmup,

        clearCache:
            clearGetCache
    };

})();w