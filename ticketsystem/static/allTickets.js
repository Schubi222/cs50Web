import {createHTML, listedHTMLContainer, displayMessage} from './util.js'
document.addEventListener('DOMContentLoaded', () =>{
    loadAllPosts()
    document.getElementById('newTicket_Form').addEventListener('submit',() =>{createNewTicket()})
})

function loadAllPosts()
{
    const all_tickets_div = document.getElementById('all_tickets')
    all_tickets_div.innerHTML = ''
    const active_user = JSON.parse(document.getElementById('active_user').textContent)
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

    fetch('getalltickets')
        .then(response => response.json())
        .then(tickets => {
            if (tickets.tickets.length === 0){all_tickets_div.innerHTML = '<h3>There are currently no tickets! </h3>'; return}
            for (let i = 0; i < tickets.tickets.length; i++) {
                listedHTMLContainer(all_tickets_div, tickets.tickets[i],'all_tickets',
                    [tickets.age[i],active_user, csrf])
            }
        })
}


// function createTicketHtml(ticket,age, parent){
//     // const wrapper = createHTML(parent,'div',['all_tickets_ticket_wrapper', 'noSelect'],'')
//     // wrapper.addEventListener('click', () =>{window.location.href=`ticket/${ticket.id}`})
//
//     // const head = createHTML(wrapper,'div',['all_tickets_ticket_head'],'')
//     // const author = createHTML(head,'div',[ 'all_tickets_ticket_author'],'')
//     // const author_link = createHTML(author,'a',[ 'all_tickets_ticket_author_link'],ticket.owner)
//     // author_link.href=`profile/${ticket.owner}`
//     // createHTML(head,'div',[ 'all_tickets_ticket_age'],`${age} Days`)
//     // const status = createHTML(head,'div',[ 'all_tickets_ticket_status'],ticket.status)
//
//     // const body = createHTML(wrapper,'div',[ 'all_tickets_ticket_body'],ticket.content)
// }

function createNewTicket(){
    const form = document.getElementById('newTicket_Form')
    const textarea = document.getElementById('newTicket_Form_Textarea')
    const content_ = textarea.value
    textarea.value = ''
    const csrf = form.elements['csrfmiddlewaretoken'].value
    const imgs = document.getElementById('newTicket_Image')

    fetch('/newticket',{
        method: 'POST',
        headers: {'X-CSRFToken':csrf},
        mode:'same-origin',
        body: JSON.stringify({
            content: content_
        })
    })
        .then(response =>{response.json()
            .then(r =>{
                if (!r.error)
                    loadAllPosts()
                else{
                    displayMessage(r.message)
                }
        })
    })
}


