import {createHTML} from "./util.js";

document.addEventListener('DOMContentLoaded', () =>{
    // loadMyTickets()
})


//TODO: THINK IF AGE SHOULD ALSO BE DAYS
function loadMyTickets(){
    const div = document.getElementById('my_tickets')
    const active_user = JSON.parse(document.getElementById('active_user').textContent)

    fetch('/mytickets/get')
        .then(response=>response.json())
        .then(response =>{
            response.tickets.forEach(ticket => createMyTicketHTML(div, ticket, active_user))
        })
}

function createMyTicketHTML(parent, ticket, active_user){
    console.log(active_user)
    console.log(ticket.owner)
    const div = createHTML(parent, 'div', ['log_entry_wrapper','log_entry_myticket_wrapper'],'')

    const head = createHTML(div, 'div', ['log_entry_head','log_entry_myticket_head'],'')

    const author = createHTML(head, 'div', ['log_entry_myticket_author'],'')
    if (active_user !== ticket.owner)
    {
        const author_link = createHTML(author, 'a', ['log_entry_link','log_entry_myticket_author_link'],ticket.owner)
        author_link.href=`profile/${ticket.owner}`
    }
    else {
        author.innerHTML = ticket.owner
    }

    const creation_date = createHTML(head, 'div', ['log_entry_date'],ticket.timestamp)

    const body = createHTML(div, 'div', ['log_entry_body','log_entry_comment_body'],ticket.content)
}