import {createHTML, listedHTMLContainer, displayMessage, claimTicket} from './util.js'
document.addEventListener('DOMContentLoaded', ()=>{
    loadLog()
    document.getElementById('ticket_new_comment_form').addEventListener('submit', () =>{comment()})
    document.getElementById('claim_btn')?.addEventListener('click', () => singleTicketClaim())
    document.getElementById('reassign_btn')?.addEventListener('click', () => reassignTicket())
    document.getElementById('close_btn')?.addEventListener('click', () => closeTicket())
})
// TODO get new assignee
function reassignTicket(){
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
    const ticket = JSON.parse(document.getElementById('ticket').textContent)
    fetch(`/ticket/${ticket.id}/reassign`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrf},
        body: JSON.stringify({
            'assign_to': 'gio'
        })
    })
        .then(response => response.json())
        .then(response => {
            if (response.error) {
                displayMessage(response.message, response.error)
            } else {
                //TODO:Check ob message überhaupt auftaucht
                displayMessage(response.message, response.error)

                const div = document.getElementById('assigned_to')
                div.innerHTML = "Assigned to: "
                const profile_a = createHTML(div, 'a', ['ticket_assigned_to'],'gio')
                profile_a.href = window.location.origin+`/profile/${"gio"}`

            }
        })
}

function closeTicket() {
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
    const ticket = JSON.parse(document.getElementById('ticket').textContent)
    fetch(`/ticket/${ticket.id}/close`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrf},
        body: JSON.stringify({})
    })
        .then(response => response.json())
        .then(response => {
            if (response.error) {
                displayMessage(response.message, response.error)
            } else {
                //TODO:Check ob message überhaupt auftaucht
                displayMessage(response.message, response.error)
                location.reload()
            }
        })
}
function singleTicketClaim(){
    const ticket = JSON.parse(document.getElementById('ticket').textContent)
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
    const user = JSON.parse(document.getElementById('active_user').textContent)

    claimTicket(ticket,document.getElementById('claim_btn'),csrf)

    document.getElementById('assigned_to').innerHTML=
        `Assigned to: <a href="profile/${user.username}" className="ticket_assigned_to">${user.username}</a>`

    setTimeout(() => { loadLog()  }, 300);
}
function comment(){
    const form = document.getElementById('ticket_new_comment_form')
    const textarea = document.getElementById('ticket_new_comment_form_Textarea')
    const content_ = textarea.value
    textarea.value = ''
    const csrf = form.elements['csrfmiddlewaretoken'].value
    const imgs = document.getElementById('newTicket_Image')
    const ticket_id = form.elements['ticket_id'].value

    fetch('/newcomment',{
        method: 'POST',
        headers: {'X-CSRFToken':csrf},
        mode:'same-origin',
        body: JSON.stringify({
            content: content_,
            ticket: ticket_id
        })
    })
        .then(response =>response.json())
        .then(r =>{
            if (!r.error) {
                loadLog()
            }

            else{
                displayMessage(r.message, r.error)
            }
        })
}

function loadLog(){
    const ticket = JSON.parse(document.getElementById('ticket').textContent)
    const parent = document.getElementById('ticket_log')
    parent.innerHTML = ''

    fetch(`/getallentries/${ticket.id}`)
        .then(response => response.json())
        .then(r =>{
            if (r.entries.length !== 0){
                createHTML(parent,'h1',['home_heading'],'Log')
            }
            r.entries.forEach(entry=>{
                switch (entry.type) {
                    case '':
                        console.log("singleTicket:loadLog: type empty")
                        break
                    case "Comment":
                        listedHTMLContainer(parent, entry, 'comment')
                        break
                    case "Notification":
                        listedHTMLContainer(parent, entry, 'notification')
                        break
                }
            })

        })


}
