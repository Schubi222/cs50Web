
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
    console.log(content)
}


//TODO: See if keeping author div for notification is fine

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

    if (type.includes('ticket') && additional[1]?.permission.includes('Worker') && !model.assigned_to){
        const claim_btn = createHTML(wrapper, 'button', ['container_claim_btn', `${type}_claim_btn`],
            'Claim Ticket')
        claim_btn.addEventListener('click',() =>{claimTicket(model,claim_btn, additional[2])})
    }

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

    if (type.includes('ticket'))
    {
        wrapper.addEventListener('click', () =>{window.location.href=`${window.location.origin}/ticket/${model.id}`})
        const status = createHTML(head,'div',[ 'container_ticket_status',`${type}_ticket_status`],model.status)
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