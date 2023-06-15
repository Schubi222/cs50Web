document.addEventListener('DOMContentLoaded', ()=>{

    document.getElementById('layout_menu_hamburger_wrapper').addEventListener('click', () =>{layout()})
    makeLayoutLinksClickable()
    document.getElementById('layout_profile')?.addEventListener('click', () => {
        const user = JSON.parse(document.getElementById('active_user').textContent)
        window.location = `${window.origin}/profile/${user.username}`
    })
    const message = document.getElementById('message_div')
    const observer = new MutationObserver(messageFade);
    const observerOptions = {childList: true,characterData:true, attributes: false, subtree: false};
    observer.observe(message,observerOptions);
    if (localStorage.getItem("message_store")){message.innerHTML=localStorage.getItem("message_store")}
    console.log(message_store)
    console.log(localStorage.getItem("message_store"))
})
let message_store = localStorage.getItem("message_store");
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
function messageFade(error=true){
    const message = document.getElementById('message_div')
    console.log(message.innerHTML)
    localStorage.setItem("message_store", message.innerHTML);

    message.classList.add('message_visible')
    const error_ = JSON.parse(document.getElementById('custom_error').textContent)
    console.log(error_)

    setTimeout(() => {  message.classList.remove('message_visible');
        localStorage.setItem("message_store", null); }, 5000);
}
function makeLayoutLinksClickable()
{
    const LIs = document.getElementsByClassName('layout_menu_li')

    Array.from(LIs).forEach(li => {
        const url = window.location.origin+'/'+li.dataset.url
        li.addEventListener('click', () =>{window.location.replace(url)})

    })
}
