
/***
 * Can be used to create any element
 * @param parent
 * @param type what type of HTML Element it should be for instance Div
 * @param classnames hast to be a list but can be an empty list
 * @param content can be empty
 * @returns {HTMLElement}
 */
export function createHTML(parent,type, classnames, content){
    let elem = document.createElement(`${type}`)
    classnames.forEach(name => elem.classList.add(name))
    elem.innerHTML = content
    parent.append(elem)
    return elem
}

export function displayMessage(content, error){

    const message = document.getElementById('message_div')
    message.innerHTML = content
    let error_ = document.getElementById('custom_error')
    error_.textContent = error.toString()
}

/***
 * 
 * @param parent parent HTML element
 * @param model the DB entry that contains all info
 * @param type what it is (will be represented in the specific classes and might be needed for additional configs)
 * having 'ticket' as part of the name will have an effect on the outcome.
 * @param additional optional | if there is any additional data that is needed; 0: ages 1: active user
 */
export function listedHTMLContainer(parent, model, type, additional=[]){
    const author_special = ['my_ticket', 'notification']

    const wrapper = createHTML(parent, 'div', ['container_wrapper', 'noSelect', `${type}_wrapper`],'')


    const head = createHTML(wrapper, 'div', ['container_head',`${type}_head`],'')

    const author = createHTML(head, 'div', ['container_author',`${type}_author`],'')

    if (!author_special.includes(type) || (type === 'my_ticket' && additional[1] !== model.owner))
    {
        const author_link = createHTML(author, 'a', ['container_author_link',`${type}_author_link`],model.owner)
        author_link.href=`profile/${model.owner}`
    }
    else if(type === 'my_ticket') {
        author.innerHTML = model.owner
    }

    const creation_date = createHTML(head, 'div', ['container_date',`${type}_date`],
        type.includes('ticket') ? `${additional[0]} Days` : model.timestamp)

    const right_head = createHTML(head,'div',[ 'container_right_head',`${type}_right_head`],'')

    if (type.includes('ticket') && additional[1]?.permission.includes('Worker') && !model.assigned_to){
        const claim_btn = createHTML(right_head, 'button', ['container_claim_btn', `${type}_claim_btn`, 'btn'],
            'Claim Ticket')
        claim_btn.addEventListener('click',() =>{claimTicket(model,claim_btn, additional[2])})
    }

    //Delay exists to reduce risk of claim happening after ticket load
    if (type.includes('ticket'))
    {
        wrapper.addEventListener('click', () =>{setTimeout(() => {
            window.location.replace(`${window.location.origin}/ticket/${model.id}`)}, 300)
        })
        const status = createHTML(right_head,'div',[ 'container_ticket_status',`${type}_ticket_status`],model.status)
    }

    const body = createHTML(wrapper, 'div', ['container_body',`${type}_body`],model.content)
    if(type === "comment"){

        const img = createHTML(body, 'img', ['container_img',`${type}_body`],'')
        img.src = model.image
    }
}


export function claimTicket(ticket, btn, csrf){
    fetch(`${window.location.origin}/ticket/${ticket.id}/claim`, {
        method: 'PUT',
        headers:{'X-CSRFToken': csrf},
        body: JSON.stringify({})
    })
        .then(response => response.json())
        .then(response =>{
            if (response.error){
                displayMessage(response.message, response.error)
            }
            else{
                displayMessage(response.message, response.error)
                btn.remove()
            }
        })
}

export function pagination(response, func, parent){
    const current_page = response.page.current
    const has_next = response.page.has_next
    const has_previous = response.page.has_previous
    const total = response.page.total

    const pagination_btn_wrapper = createHTML(parent, 'div',['pagination_btn_wrapper'],'')

    createHTML(pagination_btn_wrapper,'div',['page_of_max'],`${current_page} of ${total}`)

    if(has_previous){
        const prev_btn = createHTML(pagination_btn_wrapper, 'button', ['btn'],'Previous')
        prev_btn.addEventListener('click', ()=>{func(current_page-1)})
    }

    if(has_next){
        const next_btn = createHTML(pagination_btn_wrapper, 'button', ['btn'],'Next')
        next_btn.addEventListener('click', ()=>{func(current_page+1)})
    }
}