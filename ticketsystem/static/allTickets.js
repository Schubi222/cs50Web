document.addEventListener('DOMContentLoaded', () =>{
    loadAllPosts()
    document.getElementById('newTicket_Form').addEventListener('submit',() =>{createNewTicket()})
})

function loadAllPosts()
{
    const all_tickets_div = document.getElementById('all_tickets')
    fetch('getalltickets')
        .then(response => response.json())
        .then(tickets => {
            console.log(tickets)
            if (tickets.tickets.length === 0){all_tickets_div.innerHTML = '<h3>There are currently no tickets! </h3>'; return}
            for (let i = 0; i < tickets.tickets.length; i++) {
                createTicketHtml(tickets.tickets[i],tickets.age[i],all_tickets_div)
            }
        })

}


function createTicketHtml(ticket,age, parent){
    const wrapper = createHTML(parent,'div',['all_tickets_ticket_wrapper'],'')
    wrapper.addEventListener('click', () =>{window.location.href=`ticket/${ticket.id}`})

    const head = createHTML(wrapper,'div',['all_tickets_ticket_head'],'')
    const author = createHTML(head,'div',[ 'all_tickets_ticket_author'],'')
    const author_link = createHTML(author,'a',[ 'all_tickets_ticket_author_link'],ticket.owner)
    author_link.href=`profile/${ticket.owner}`
    createHTML(head,'div',[ 'all_tickets_ticket_age'],`${age} Days`)
    const status = createHTML(head,'div',[ 'all_tickets_ticket_status'],ticket.status)
    const body = createHTML(wrapper,'div',[ 'all_tickets_ticket_body'],ticket.content)
}

function createNewTicket(){
    const form = document.getElementById('newTicket_Form')
    const content_ = document.getElementById('newTicket_Form_Textarea').value
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

        })
    })
}


/***
 * Can be used to create any element
 * @param parent
 * @param type what type of HTML Element it should be for instance Div
 * @param classnames hast to be a list but can be an empty list
 * @param content can be empty
 * @returns {HTMLElement}
 */
function createHTML(parent,type, classnames, content){
    let elem = document.createElement(`${type}`)
    classnames.forEach(name => elem.classList.add(name))
    elem.innerHTML = content
    parent.append(elem)
    return elem
}