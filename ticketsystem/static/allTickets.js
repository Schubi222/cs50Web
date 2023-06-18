import {createHTML, listedHTMLContainer, displayMessage, pagination} from './util.js'
document.addEventListener('DOMContentLoaded', () =>{
    loadAllPosts()
    document.getElementById('newTicket_Form').addEventListener('submit',() =>{createNewTicket()})
})

function loadAllPosts(page_number=1)
{
    const all_tickets_div = document.getElementById('all_tickets')
    all_tickets_div.innerHTML = ''
    const active_user = JSON.parse(document.getElementById('active_user').textContent)
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value

    fetch(`getalltickets/${page_number}`)
        .then(response => response.json())
        .then(tickets => {
            if (tickets.tickets.length === 0){all_tickets_div.innerHTML = '<h3>There are currently no tickets! </h3>'; return}

            for (let i = 0; i < tickets.tickets.length; i++) {
                listedHTMLContainer(all_tickets_div, tickets.tickets[i],'all_tickets',
                    [tickets.age[i],active_user, csrf])
            }
            pagination(tickets,loadAllPosts,all_tickets_div)
        })
}
function createNewTicket(){
    const form = document.getElementById('newTicket_Form')
    const textarea = document.getElementById('newTicket_Form_Textarea')
    const content_ = textarea.value
    if (content_ === "")
    {
        displayMessage('Please enter a message', true)
        return
    }
    textarea.value = ''
    const csrf = form.elements['csrfmiddlewaretoken'].value
    const img_html = document.getElementById('newTicket_Image')
    const img = img_html.value
    img_html.value = ''

    fetch('/newticket',{
        method: 'POST',
        headers: {'X-CSRFToken':csrf},
        mode:'same-origin',
        body: JSON.stringify({
            content: content_,
            image: img,
        })
    })
        .then(response =>{response.json()
            .then(r =>{
                if (!r.error)
                    loadAllPosts()
                else{
                    displayMessage(r.message, r.error)
                }
        })
    })
}


