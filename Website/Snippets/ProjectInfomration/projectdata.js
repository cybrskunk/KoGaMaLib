const PID = 'ProjectID'; 
fetch(`https://www.kogama.com/game/${PID}/member`)
  .then(res => res.json())
  .then(({ data }) => 
    console.log(`Game: ${data[0]?.name}\nMembers:\n` + 
      data.map(m => `${m.member_username} (${m.member_user_id})`).join('\n'))
  )
  .catch(err => console.error('Fetch error:', err));

// Output example;
// Game: TITLE
// Members:
// P (USERID)
// Λ. (USERID)
// A. (USERID)
