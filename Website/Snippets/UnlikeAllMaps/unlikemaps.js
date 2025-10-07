const UID = 'OwnUserID';
fetch('https://www.kogama.com/game/category/likes/?page=1&count=77')
  .then(response => response.json())
  .then(async data => {
    const games = data.data;
    const totalGames = games.length;

    for (let i = 0; i < totalGames; i++) {
      const gameId = games[i].id;
      const deleteUrl = `https://www.kogama.com/game/${gameId}/like/${UID}/`;

      try {
        const deleteResponse = await fetch(deleteUrl, { method: 'DELETE' });
        if (deleteResponse.ok) {
          console.log(`${i + 1} / ${totalGames} unliked`);
        } else {
          console.log(`Error: Failed to unlike game ID ${gameId}`);
        }
      } catch (error) {
        console.error(`Error: Unable to send DELETE request for game ID ${gameId} - ${error}`);
      }
    }
  })
  .catch(error => {
    console.error('Error fetching the game data:', error);
  });

// This allows us to unlike each of our liked maps. Code is kinda janky, can be shortened and improved. It works tho, so I'm sticking to this.
