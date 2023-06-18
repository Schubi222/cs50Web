import {createHTML, listedHTMLContainer, displayMessage, pagination} from './util.js'
document.addEventListener("DOMContentLoaded", ()=>{
    loadProfile()
})

function loadProfile(){
    const user_of_profile = JSON.parse(document.getElementById('user_of_profile').textContent)

    const profile_header_wrapper = document.getElementById('profile_header_wrapper')
    const profile_header_ticket_count = document.getElementById('profile_header_ticket_count')

    document.getElementById('profile_circle').innerHTML = user_of_profile.username.substring(0,3)

    fetch(`/profile/${user_of_profile.username}/infos`)
        .then(response => response.json())
        .then(response =>{
            if (response.error)
            {
                displayMessage(response.message, response.error)
                return
            }
            profile_header_ticket_count.innerHTML += response.ticket_count

            if (user_of_profile.permission.includes('Worker')){
                createHTML(profile_header_wrapper, 'div', ['profile_header_ticket_assigned_count'],
                    `Number of open tickets: ${response.assigned_ticket_count}`)
            }
        })

        ticket()

        if (user_of_profile.permission === "User"){return}

        assigned()
}

function ticket(page=1){
    const user_of_profile = JSON.parse(document.getElementById('user_of_profile').textContent)
        const active_user = JSON.parse(document.getElementById('active_user').textContent)
    fetch(`/profile/${user_of_profile.username}/ticket/${page}`)
            .then(response => response.json())
            .then(response =>{
                if (response.error)
                {
                    displayMessage(response.message, response.error)
                    return
                }
                const parent = document.getElementById('profile_created_tickets')
                parent.innerHTML = ''
                createHTML(parent, 'h2', ['profile_tickets_heading'],
                `${user_of_profile.username}\'s Tickets`)
                if (response.tickets.length === 0)
                {
                    createHTML(parent, 'h4', [],'There are no open tickets from this user!')
                }
                for (let i = 0; i < response.tickets.length; i++) {
                    listedHTMLContainer(parent, response.tickets[i], 'profile_created_tickets',
                        [response.ages[i], active_user])
                }
                pagination(response,ticket,parent)
            })
}
function assigned(page=1){
    const user_of_profile = JSON.parse(document.getElementById('user_of_profile').textContent)
        const active_user = JSON.parse(document.getElementById('active_user').textContent)
    fetch(`/profile/${user_of_profile.username}/assigned/${page}`)
        .then(response => response.json())
        .then(response =>{
            if (response.error)
            {
                displayMessage(response.message, response.error)
                return
            }
            const parent = document.getElementById('profile_assigned_tickets')
            parent.innerHTML = ''

            createHTML(parent, 'h2', ['profile_tickets_heading'],
                `Tickets assigned to ${user_of_profile.username}`)

            if (response.tickets.length === 0)
            {
                createHTML(parent, 'h4', [],'This worker does not have any tickets assigned!')
            }
            for (let i = 0; i < response.tickets.length; i++) {
                listedHTMLContainer(parent, response.tickets[i], 'profile_assigned_tickets',
                    [response.ages[i], active_user])
            }
            pagination(response,assigned, parent)
        })
}