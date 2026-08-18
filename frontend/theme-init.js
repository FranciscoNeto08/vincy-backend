(function(){
    "use strict";
    const key = "vincy_tema";
    let tema = localStorage.getItem(key);
    if(tema !== "claro" && tema !== "escuro"){
        tema = "claro";
        localStorage.setItem(key, tema);
    }
    document.documentElement.setAttribute("data-theme", tema);
})();
