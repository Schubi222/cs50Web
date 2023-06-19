import {createHTML, displayMessage, listedHTMLContainer, pagination} from './util.js'
document.addEventListener('DOMContentLoaded', () =>{
    loadMyTeam()
    document.getElementById('myTeam_new_team')?.addEventListener('click', () => newTeam())
})
function newTeam(){
    const active_user = JSON.parse(document.getElementById('active_user').textContent)
    if (active_user.permission !== "Lead_Worker"){
        displayMessage('You do not have the permission to do that!')
        return
    }
    document.getElementById('myTeam_Team').innerHTML = ""
    document.getElementById('myTeam_Team_Tickets').innerHTML = ""
    document.getElementById('myTeam_create_worker').style.display = "none"
    document.getElementById('myTeam_new_team').style.display = "none"

    document.getElementById('back_btn_team').addEventListener('click', () => loadMyTeam(),
        { once: true })


    document.getElementById('myTeam_create_team').style.display = "flex"
}
function loadMyTeam(){

    const active_user = JSON.parse(document.getElementById('active_user').textContent)
    if (!active_user || active_user.permission === "User")
    {
        displayMessage('You do not have the permission to do that!', true) //TODO: Hier wieder die frage ob das übrhpt da is
        window.location = window.location.origin
        return
    }
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
    const team_div = document.getElementById('myTeam_Team')
    const ticket_div = document.getElementById('myTeam_Team_Tickets')
    team_div.innerHTML = ''
    ticket_div.innerHTML = ''

    document.getElementById('myTeam_create_worker').style.display = "none"
    document.getElementById('myTeam_create_team').style.display = "none"
    document.getElementById('myTeam_new_team').style.display = "unset"
    loadTeam(team_div)
    loadTeamTickets()
}

function loadTeam(parent){

    parent.innerHTML = ''

    fetch('/myteam/team')
        .then(response => response.json())
        .then(response => {
            if (response.error)
            {
                displayMessage(response.message, response.error)
                return
            }
            const active_user = JSON.parse(document.getElementById('active_user').textContent)

            createHTML(parent,"h2", ['myTeam_h2'],'Team Leader')

            const leader_parent = createHTML(parent,'div',
                    ['myTeam_general_all_wrapper','myTeam_leader_all_wrapper'],'')

            if (response.leader.length !== 0){

                response.leader.forEach(leader => {
                createHTMLForWorker('leader',leader,leader_parent)
                })

            }

            if(active_user.permission === "Lead_Worker") {
                createHTMLAddWorker(leader_parent, "Lead_Worker")
            }

            createHTML(parent,"h2", ['myTeam_h2'],'Team Member')

            const worker_parent = createHTML(parent,'div',
            ['myTeam_general_all_wrapper','myTeam_worker_all_wrapper'],'')

            if (response.member.length !== 0){

                response.member.forEach(member =>{
                    createHTMLForWorker('worker', member, worker_parent)
                })

            }

            if(active_user.permission === "Lead_Worker") {
                createHTMLAddWorker(worker_parent, "Worker")
            }
        })
}

function loadTeamTickets( page=1){
    const parent = document.getElementById('myTeam_Team_Tickets')
    parent.innerHTML = ''
    const user = JSON.parse(document.getElementById('active_user').textContent)
    const team = user.leader_of ? user.leader_of : user.member_of
    if (!team){
        createHTML(parent, "h2", [],`You are currently not part of any team!`)
        return
    }
    createHTML(parent, "h2", [],`Tickets of Team ${team}`)
    fetch(`/myteam/tickets/${page}`)
        .then(response => response.json())
        .then(response => {
            if (response.error)
            {
                displayMessage(response.message, response.error)
                return
            }
            if (response.tickets.length === 0){
                createHTML(parent, "h3", [],'This team does not have any assigned tickets!')
                return
            }
            for (let i = 0; i < response.tickets.length; i++) {
                listedHTMLContainer(parent,response.tickets[i],'myTeam_ticket',[response.ages[i],user])
            }
            pagination(response,loadTeamTickets,parent)
        })
}

function loadCreateWorker(permission){
    document.getElementById('myTeam_Team').innerHTML = ""
    document.getElementById('myTeam_Team_Tickets').innerHTML = ""
    document.getElementById('myTeam_create_team').style.display = "none"
    document.getElementById('myTeam_new_team').style.display = "none"

    document.getElementById('back_btn').addEventListener('click', () => loadMyTeam(),
        { once: true })

    const heading = document.getElementById('myTeam_create_worker_heading')

    const permission_name = permission === 'Lead_Worker' ? "Team Leader" : "Worker"
    heading.innerHTML = `Create a new ${permission_name}`

    document.getElementById(permission).checked = true

    document.getElementById('myTeam_create_worker').style.display = "flex"
}

function createHTMLForWorker(role,user,parent){

    const wrapper = createHTML(parent, 'div', [`myTeam_general_wrapper`],'')
    wrapper.addEventListener('click', () => {
        window.location = `${window.location.origin}/profile/${user.username}`
    })
    createHTML(wrapper, 'div', [`myTeam_general_circle`, `myTeam_${role}_circle`], user.username.substring(0,3))

    createHTML(wrapper, 'div', [`myTeam_general_name`, `myTeam_${role}_name`], user.username)
}

function createHTMLAddWorker(parent, permission){
    const wrapper = createHTML(parent, 'div', [`myTeam_general_wrapper`],'')
    wrapper.addEventListener('click', () => { loadCreateWorker(permission) })
    createHTML(wrapper, 'div', [`myTeam_general_circle`], "+")

    createHTML(wrapper, 'div', [`myTeam_general_name`], 'Add')
}