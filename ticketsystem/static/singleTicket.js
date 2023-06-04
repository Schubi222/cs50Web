import {createHTML, displayMessage} from './util.js'
document.addEventListener('DOMContentLoaded', ()=>{
    loadLog()
    document.getElementById('ticket_new_comment_form').addEventListener('click', () =>{comment()})
})

function comment(){
    const form = document.getElementById('ticket_new_comment_form')
    const textarea = document.getElementById('ticket_new_comment_form_Textarea')
    const content_ = textarea.value
    textarea.value = ''
    const csrf = form.elements['csrfmiddlewaretoken'].value
    const imgs = document.getElementById('newTicket_Image')

    fetch('/newcomment',{
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
                    loadLog()
                else{
                    displayMessage(r.message)
                }
        })
    })
}

function loadLog(){
    const ticket = JSON.parse(document.getElementById('ticket').textContent)
    const log = ticket.log
    const parent = document.getElementById('ticket_log')
    log.forEach(entry => {
        switch (entry.type) {
            case '':
                console.log("singleTicket:loadLog: type empty")
                break
            case "Comment":
                createCommentHTML(parent, entry)
                break
            case "Notification":
                createNotificationHTML(parent, entry)
                break
        }
    })

}

function createCommentHTML(parent, entry){
    const div = createHTML(parent, 'div', ['log_entry_wrapper','log_entry_comment_wrapper'],'')

    const head = createHTML(div, 'div', ['log_entry_head','log_entry_comment_head'],'')

    const author = createHTML(head, 'div', ['log_entry_comment_author'],'')
    const author_link = createHTML(author, 'a', ['log_entry_link','log_entry_comment_author_link'],entry.owner)
    author_link.href=`profile/${entry.owner}`
    const creation_date = createHTML(head, 'div', ['log_entry_date'],entry.timestamp)

    const body = createHTML(div, 'div', ['log_entry_body','log_entry_comment_body'],entry.content)

}

function createNotificationHTML(parent, entry){
    const div = createHTML(parent, 'div', ['log_entry_wrapper','log_entry_notification_wrapper'],'')

    const head = createHTML(div, 'div', ['log_entry_head','log_entry_notification_head'],'')

    const creation_date = createHTML(head, 'div', ['log_entry_date'],entry.timestamp)

    const body = createHTML(div, 'div', ['log_entry_body','log_entry_notification_body'],entry.content)
}