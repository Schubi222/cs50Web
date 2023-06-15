import {createHTML, listedHTMLContainer, displayMessage, claimTicket} from './util.js'
document.addEventListener('DOMContentLoaded', ()=>{
    loadLog()
    document.getElementById('ticket_new_comment_form').addEventListener('submit', () =>{comment()})
    document.getElementById('claim_btn')?.addEventListener('click', () => singleTicketClaim())
    document.getElementById('reassign_btn')?.addEventListener('click', () => openReassignSelect(),
        { once: true })
    document.getElementById('close_btn')?.addEventListener('click', () => closeTicket())
})


function openReassignSelect (){
    document.getElementById('assigned_span').style.display="none"

    const select_elem = document.getElementById('assign_select');
    select_elem.style.display="unset"
    if (select_elem.options.length !== 0 )
    {
        const length = select_elem.options.length
        for (let i = 0; i < length; i++) {
            select_elem[0].remove()
        }
    }

    fetch(`${window.location.origin}/myteam/team`)
        .then(response => response.json())
        .then(response => {
            if (response.error) {
                displayMessage(response.message)
            }
            else{
                select_elem.add(new Option('unassign','unassign'));

                response.leader.forEach(leader => {
                    select_elem.add(new Option(leader.username,leader.username))
                })
                response.member.forEach(member => {
                    select_elem.add(new Option(member.username,member.username))
                })
            }
        })

    document.getElementById('reassign_btn')?.addEventListener('click', () => reassignTicket(),
        { once: true })
}

function reassignTicket(){
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
    const ticket = JSON.parse(document.getElementById('ticket').textContent)
    const select = document.getElementById('assign_select')
    const user = select.value

    fetch(`/ticket/${ticket.id}/reassign`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrf},
        body: JSON.stringify({
            'assign_to': user
        })
    })
        .then(response => response.json())
        .then(response => {
            document.getElementById('assigned_span').style.display="unset"
            if (response.error) {
                displayMessage(response.message, response.error)
                if(ticket.assigned_to){
                    const a = document.getElementById('ticket_assigned_to')
                    a.innerHTML=ticket.assigned_to
                    a.href = window.location.origin+`/profile/${ticket.assigned_to}`
                }
                else{
                    document.getElementById('assigned_span').innerHTML = `Not yet assigned`
                }
                 select.style.display="none"
                document.getElementById('reassign_btn')?.addEventListener('click',
                    () => openReassignSelect(), { once: true })
                loadLog()
                return;
            }

            //TODO:Check ob message überhaupt auftaucht
            displayMessage(response.message, response.error)
            if(user !== "unassign"){

                select.style.display="none"

                document.getElementById('assigned_span').style.display="unset"
                document.getElementById('assigned_span').innerHTML=
                `<a href="${window.location.origin}/profile/${user}" className="ticket_assigned_to">${user}</a>`

                document.getElementById('reassign_btn').style.display = "unset"

                document.getElementById('reassign_btn')?.addEventListener('click',
                    () => openReassignSelect(), { once: true })

                loadLog()
                return
            }
            else{
                document.getElementById('assigned_span').innerHTML = `Not yet assigned`

                document.getElementById('reassign_btn').remove()

                const btn = createHTML(document.getElementById('btn_span'),'button',['btn'],
                    'Claim')
                btn.id = "claim_btn"
                btn.addEventListener('click', () => singleTicketClaim())
            }

            select.style.display="none"
            loadLog()
            document.getElementById('reassign_btn')?.addEventListener('click',
                () => openReassignSelect(), { once: true })
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

    document.getElementById('assigned_span').innerHTML=
        `<a href="${window.location.origin}/profile/${user.username}" className="ticket_assigned_to">${user.username}</a>`

    const btn = createHTML(document.getElementById('btn_span'),'button',['btn'],
        'Reassign')

    btn.id = "reassign_btn"
    btn.addEventListener('click', () => openReassignSelect(), { once: true })

    setTimeout(() => { loadLog()  }, 300);
}
function comment(){
    const form = document.getElementById('ticket_new_comment_form')
    const textarea = document.getElementById('ticket_new_comment_form_Textarea')
    const content_ = textarea.value
    textarea.value = ''
    const csrf = form.elements['csrfmiddlewaretoken'].value

    const img_html = document.getElementById('ticket_new_comment_image')
    const img = img_html.value
    img_html.value = ''
    
    const ticket_id = form.elements['ticket_id'].value

    fetch('/newcomment',{
        method: 'POST',
        headers: {'X-CSRFToken':csrf},
        mode:'same-origin',
        body: JSON.stringify({
            content: content_,
            ticket: ticket_id,
            image: img
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
