document.addEventListener('DOMContentLoaded', () =>{
    loadAllPosts()
})

function loadAllPosts()
{
    const all_tickets_div = document.getElementById('all_tickets')
    fetch('getalltickets')
        .then(response => response.json())
        .then(tickets => {
            console.log(tickets)
            console.log(tickets.length)
            if (tickets.tickets.length === 0){all_tickets_div.innerHTML = '<h3>There are currently no tickets! </h3>'; return}
            tickets.tickets.forEach(ticket => createTicketHtml(ticket,all_tickets_div))
        })

}
/*

        <div class="all_tickets_ticket_wrapper">
            <div class="all_tickets_ticket_head">
                <div class="all_tickets_ticket_author"><a class="all_tickets_ticket_author_link" href="#">User</a> </div>
                <div class="all_tickets_ticket_age">15 Days old</div>
                <div class="all_tickets_ticket_status">Done</div>
            </div>
            <div class="all_tickets_ticket_body">My PC isn't working.</div>
        </div>
* */
function createTicketHtml(data, parent){
    console.log(data.timestamp)
    const wrapper = createHTML(parent,'div','all_tickets_ticket_wrapper','')
    wrapper.addEventListener('click', () =>{window.location.href=`ticket/${data.id}`})

    const head = createHTML(wrapper,'div','all_tickets_ticket_head','')
    const author = createHTML(head,'div','all_tickets_ticket_author','')
    const author_link = createHTML(author,'a','all_tickets_ticket_author_link',data.author)
    author_link.href=`profile/${data.author}`
    const age = createHTML(head,'div','all_tickets_ticket_age','')
    const status = createHTML(head,'div','all_tickets_ticket_status',data.status)
    const body = createHTML(wrapper,'div','all_tickets_ticket_body',data.content)
}

/***
 * Can be used to create any element
 * @param parent
 * @param type what type of HTML Element it should be for instance Div
 * @param classnames can be empty and can be a list
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