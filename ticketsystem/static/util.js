
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