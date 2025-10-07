const userId = "OwnUserID"; 
const username = "newUsername"; 

fetch("https://www.kogama.com/user/" + userId + "/username/", {
    method: "POST",
    headers: {
        "content-type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify({ "username": username }),
    credentials: "include"
})


// This snippet allows us to change our profile username without the need to confirm our email.
// STILL REQUIRES 25 GOLD.
// Credits to @zpayer for providing the base snippet.
