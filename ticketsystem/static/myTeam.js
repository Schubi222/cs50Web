import {createHTML, displayMessage} from './util.js'
document.addEventListener('DOMContentLoaded', () =>{
    loadMyTeam()
})

function loadMyTeam(){
    const active_user = JSON.parse(document.getElementById('active_user').textContent)
    if (!active_user || active_user.permission === "User")
    {
        displayMessage('You do not have the permission to do that!') //TODO: Hier wieder die frage ob das übrhpt da is
        window.location = window.location.origin
        return
    }
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
    const team_div = document.getElementById('myTeam_Team')
    const ticket_div = document.getElementById('myTeam_Team_Tickets')
    loadTeam(team_div, active_user, active_user.team, csrf)
    loadTeamTickets(ticket_div, active_user, active_user.team)
}

function loadTeam(parent, user, team, csrf){
    fetch('/myteam/team')
        .then(response => response.json())
        .then(response => {
            if (response.error)
            {
                displayMessage(response.message)
                return
            }
            for (const leader in response.leader) {
                createHTMLForWorker('leader',leader,parent)
            }
            for (const member in response.member) {
                createHTMLForWorker('worker', member, parent)
            }
        })

}

function loadTeamTickets(parent, user, team){

}

function createHTMLForWorker(role,user,parent){
    const wrapper = createHTML(parent, 'div', [`myTeam_general_wrapper`],'')
    wrapper.addEventListener('click', () => {
        window.location = `${window.location.origin}/profile/${user.username}`
    })
    createHTML(parent, 'div', [`myTeam_general_circle`, `myTeam_${role}_circle`], user.username.substring(0,3))

    createHTML(parent, 'div', [`myTeam_general_name`, `myTeam_${role}_name`], user.username)
}