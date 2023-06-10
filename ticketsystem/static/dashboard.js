document.addEventListener("DOMContentLoaded", ()=>{
    loadDashboard()
})

function loadDashboard(){
    fetch('/mydashboard/get')
        .then(response => response.json())
        .then(response => {
            console.log(response)
        })
}