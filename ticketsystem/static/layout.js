document.addEventListener('DOMContentLoaded', ()=>{

    document.getElementById('layout_menu_hamburger_wrapper').addEventListener('click', () =>{layout()})
    makeLayoutLinksClickable()
    document.getElementById('layout_profile')?.addEventListener('click', () => loadProfile())
    const message = document.getElementById('message_div')
    if (message) {messageFade(message)}
})
let open = false
function layout(){
    const before = document.getElementById('layout_menu_hamburger_before')
    const middle = document.getElementById('layout_menu_hamburger_middle')
    const after = document.getElementById('layout_menu_hamburger_after')
    const menu_div = document.getElementById('layout_menu_ul')
    const menu_lis = document.getElementsByClassName('layout_menu_li')
    if (open){
        open = false
        before.classList.remove('is_open')
        middle.classList.remove('is_open')
        after.classList.remove('is_open')
        menu_div.classList.remove('is_open')
        Array.from(menu_lis).forEach(li => li.classList.remove('is_open'))
    }else{
        open = true
        before.classList.add('is_open')
        middle.classList.add('is_open')
        after.classList.add('is_open')
        menu_div.classList.add('is_open')
        Array.from(menu_lis).forEach(li => li.classList.add('is_open'))
    }
}
function messageFade(){

}
function makeLayoutLinksClickable()
{
    const LIs = document.getElementsByClassName('layout_menu_li')

    Array.from(LIs).forEach(li => {
        const url = window.location.origin+'/'+li.dataset.url
        li.addEventListener('click', () =>{window.location.replace(url)})

    })
}

function loadProfile(){
    const user = JSON.parse(document.getElementById('active_user').textContent)
    window.location = `${window.origin}/profile/${user.username}`
}