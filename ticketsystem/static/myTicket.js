import {createHTML, listedHTMLContainer, displayMessage} from "./util.js";

document.addEventListener('DOMContentLoaded', () =>{
    loadMyTickets()
})


//TODO: THINK IF AGE SHOULD ALSO BE DAYS
function loadMyTickets(){
    const div = document.getElementById('my_tickets')
    const active_user = JSON.parse(document.getElementById('active_user').textContent)
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

    fetch('/mytickets/get')
        .then(response=>response.json())
        .then(response =>{
            const user_tickets = response.user_tickets
            const worker_tickets = response.worker_tickets

            createHTML(div, 'h2', ['my_tickets_heading'],'My tickets')

            if (user_tickets.tickets === null)
                createHTML(div, 'h3', [],'There are currently no tickets!')

            for (let i = 0; i < user_tickets.tickets?.length; i++) {

                const age = user_tickets.ages[i]
                const ticket = user_tickets.tickets[i]

                listedHTMLContainer(div, ticket,'my_ticket', [age, active_user, csrf])
            }

            if (response.worker_tickets.tickets)
                createHTML(div, 'h2', ['my_tickets_heading'],'My assigned tickets')

            for (let i = 0; i < worker_tickets.tickets?.length; i++) {

                const age = worker_tickets.ages[i]
                const ticket = worker_tickets.tickets[i]

                listedHTMLContainer(div, ticket,'my_ticket', [age, active_user, csrf])
            }
        })
}