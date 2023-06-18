import {listedHTMLContainer, pagination} from './util.js'
document.addEventListener('DOMContentLoaded',() =>{
   loadArchive()
})

function loadArchive(page=1){
    const parent = document.getElementById('all_archive')
    parent.innerHTML = ''
    const active_user = JSON.parse(document.getElementById('active_user').textContent)
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
    fetch(`archive/get/${page}`)
        .then(response => response.json())
        .then(response =>{


            if (response.tickets.length === 0){parent.innerHTML = '<h3>There are currently no tickets in the archive! </h3>'; return}
            for (let i = 0; i < response.tickets.length; i++) {
                listedHTMLContainer(parent, response.tickets[i],'all_tickets',
                    [response.age[i],active_user, csrf])
            }
            pagination(response,loadArchive,parent)

        })
}