import {createHTML, listedHTMLContainer, displayMessage, pagination} from "./util.js";

document.addEventListener('DOMContentLoaded', () =>{
    loadMyTickets()
})

function loadMyTickets(){

    loadUser()
    loadWorker()
}

function loadUser(page=1){
    const div = document.getElementById('my_tickets_user')
    div.innerHTML=''
    const active_user = JSON.parse(document.getElementById('active_user').textContent)
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

    fetch(`/mytickets/user/${page}`)
        .then(response=>response.json())
        .then(response =>{
            createHTML(div, 'h2', ['my_tickets_heading'],'My tickets')

            if (response.tickets.length === 0) {
                createHTML(div, 'h3', [], 'There are currently no tickets!')
                return
            }

            for (let i = 0; i < response.tickets?.length; i++) {

                const age = response.ages[i]
                const ticket = response.tickets[i]

                listedHTMLContainer(div, ticket,'my_ticket', [age, active_user, csrf])
            }
            pagination(response, loadUser,div)
        })
}
function loadWorker(page=1){
    const div = document.getElementById('my_tickets_worker')
    div.innerHTML = ''
    const active_user = JSON.parse(document.getElementById('active_user').textContent)
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

    fetch(`/mytickets/worker/${page}`)
        .then(response=>response.json())
        .then(response =>{

            if (response.tickets.length === 0){
                return
            }

            createHTML(div, 'h2', ['my_tickets_heading'],'My assigned tickets')

            for (let i = 0; i < response.tickets?.length; i++) {

                const age = response.ages[i]
                const ticket = response.tickets[i]

                listedHTMLContainer(div, ticket,'my_ticket', [age, active_user, csrf])
            }
            pagination(response, loadWorker,div)
        })
}