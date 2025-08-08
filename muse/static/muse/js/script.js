let currentIndex = 0;
const audio = document.getElementById('audio');
const songTitle = document.getElementById('songTitle');
const artistName = document.getElementById('artistName');
const albumArt = document.getElementById('albumArt');
const songList = document.getElementById('songList');
const playBtn = document.getElementById('playPause');
const nextBtn = document.getElementById('next');
const prevBtn = document.getElementById('prev');

function loadSong(index) {
  const song = songs[index];
  if (!song) return;
  audio.src = song.src;
  songTitle.textContent = song.song_name;
  artistName.textContent = song.artist.display_name;
  albumArt.src = song.song_art.url;
  audio.load();
}

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift()
}

loadSong(currentIndex);

playBtn.addEventListener('click', () => {
  audio.paused ? audio.play() : audio.pause();
});

nextBtn.addEventListener('click', () => {
  currentIndex = (currentIndex + 1) % songs.length;
  loadSong(currentIndex);
});

prevBtn.addEventListener('click', () => {
  currentIndex = (currentIndex - 1 + songs.length) % songs.length;
  loadSong(currentIndex);
});

songList.addEventListener('click', e => {
  if (e.target.tagName === 'LI') {
    currentIndex = Number(e.target.getAttribute('data-index'));
    loadSong(currentIndex);
  }
});

// Like buttons AJAX
document.querySelectorAll('.like-comment').forEach(button => {
  const csrftoken = getCookie('csrftoken')
  button.addEventListener('click', () => {
    fetch(button.dataset.url, {
      method: 'POST',
      body: JSON.stringify({ comment_id: button.dataset.id }),
      headers: { 'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,}
    })
    .then(res => res.json())
    .then(data => {
      button.textContent = `❤️ ${data.likes}`;
    });
  });
});

// Toggle replies
document.querySelectorAll('.toggle-replies').forEach(btn => {
  btn.addEventListener('click', () => {
    const replies = btn.closest('.comment').querySelector('.replies');
    replies.classList.toggle('hidden');
    btn.textContent = replies.classList.contains('hidden') ? 'View Replies' : 'Hide Replies';
  });
});

document.querySelectorAll('.rec-play').forEach(button => {
  button.addEventListener('click', (e) => {
    const parent = button.closest('li');
    const src = parent.getAttribute('data-src');
    audio.src = src;
    audio.play();
    songTitle.textContent = parent.querySelector('.rec-title').textContent;
    artistName.textContent = parent.querySelector('.rec-artist').textContent;
    albumArt.src = parent.querySelector('.rec-cover').src;
  });
});

