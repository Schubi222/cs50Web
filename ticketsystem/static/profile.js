import {createHTML, listedHTMLContainer, displayMessage} from './util.js'
document.addEventListener("DOMContentLoaded", ()=>{
    loadProfile()
})
/*
* const wrapper = createHTML(parent, 'div', [`myTeam_general_wrapper`],'')
    wrapper.addEventListener('click', () => {
        window.location = `${window.location.origin}/profile/${user.username}`
    })
    createHTML(wrapper, 'div', [`myTeam_general_circle`, `myTeam_${role}_circle`], user.username.substring(0,3))

    createHTML(wrapper, 'div', [`myTeam_general_name`, `myTeam_${role}_name`], user.username)
*
* */
function loadProfile(){
    const user_of_profile = JSON.parse(document.getElementById('user_of_profile').textContent)
    const active_user = JSON.parse(document.getElementById('active_user').textContent)
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

        fetch(`/profile/${user_of_profile.username}/ticket`)
            .then(response => response.json())
            .then(response =>{
                if (response.error)
                {
                    displayMessage(response.message, response.error)
                    return
                }
                const parent = document.getElementById('profile_created_tickets')
                if (response.tickets.length === 0)
                {
                    createHTML(parent, 'h4', [],'There are no open tickets from this user!')
                }
                for (let i = 0; i < response.tickets.length; i++) {
                    listedHTMLContainer(parent, response.tickets[i], 'profile_created_tickets',
                        [response.ages[i], active_user])
                }
            })

        if (user_of_profile.permission === "User"){return}

        fetch(`/profile/${user_of_profile.username}/assigned`)
            .then(response => response.json())
            .then(response =>{
                if (response.error)
                {
                    displayMessage(response.message, response.error)
                    return
                }
                const parent = document.getElementById('profile_assigned_tickets')

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
            })
}