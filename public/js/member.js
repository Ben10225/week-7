let btnMessage = document.querySelector(".btn-message")
btnMessage.addEventListener("click", ()=>{
  fetchItems("message", 'POST');
});

let btnQuery = document.querySelector(".btn-query")
btnQuery.addEventListener("click", ()=>{
  fetchItems("query", 'POST');

});

let btnModify = document.querySelector(".btn-modify")
btnModify.addEventListener("click", ()=>{
  fetchItems("modify", 'PATCH');
});

let ct = 0
let lst = []

function fetchItems(routeName, method){
  let msg = document.querySelector(`#${routeName}`);
  fetch(`/${routeName}`, {
    method: method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      "msg": msg.value,
    }),
  })
  .then((response) => response.json())
  .then((data) => {
    // 留言功能
    if(data.routeName == "message"){
      if(data.feedback == "請輸入文字"){
        alert("請輸入文字");

      }else if(data.feedback == "無登入狀態"){
        window.location.href="/";

      }else if(data.feedback == "留言完成"){
        msg.value = "";
        window.location.href="/member";
      }
    }
    // 搜尋功能
    if(data.routeName == "query"){
      let span = document.querySelector(".query-result")
      if(data.feedback == "請輸入查詢姓名"){
        alert("請輸入查詢姓名");

      }else if(data.feedback == "無登入狀態"){
        window.location.href="/";

      }else if(data.feedback == "查詢成功"){
        // msg.value = "";
        span.textContent = `${data.data.name} (${data.data.username})`;


      }else if(data.feedback == "查詢失敗"){
        msg.value = "";
        span.textContent = ``;
      }
    }
    // 更新功能
    if(data.routeName == "modify"){
      if(data.feedback == "請輸入更新姓名"){
        alert("請輸入更新姓名");

      }else if(data.feedback == "更新名字請與原本不同"){
        alert("更新名字請與原本不同");

      }else if(data.feedback == "無登入狀態"){
        window.location.href="/";

      }else if(data.feedback == "更新成功"){
        ct += 1;
        msg.value = "";
        let modifyText = document.querySelector(".modify_success");
        modifyText.style.opacity = "1";
        setTimeout(()=>{
          modifyText.style.opacity = "0";
        }, 3000)
        // 更新 h2 名字
        let name = document.querySelector(".userNewName");
        name.textContent = data.newName;

        // 清除搜尋名字的紀錄
        let span = document.querySelector(".query-result");
        span.textContent = "";
        let queryInput = document.querySelector(`#query`);
        queryInput.value = "";

        // 更新留言的名字，避免改成相同名字一起變
        let messageName = document.querySelectorAll(".userName");
        if(ct == 1){
          for(let i=0;i<messageName.length;i++){
            if(messageName[i].textContent == data.oldName){
              lst.push(i)
              messageName[i].textContent = data.newName;
            }
          }
        }
        if(ct > 1){
          for(let i of lst){
            messageName[i].textContent = data.newName;
          }
        }
      }
    }
  })
}
