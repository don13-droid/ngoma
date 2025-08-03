const musicPlayer = document.querySelector('.music-player');
const albumArtImage = document.querySelector('.album-art-image');
const recordOverlay = document.querySelector('.record-overlay');
const playPauseButton = document.querySelector('.play-pause-button');
const previousButton = document.querySelector('.previous-button');
const nextButton = document.querySelector('.next-button');
const progressBar = document.querySelector('.progress-bar');
const currentTimeSpan = document.querySelector('.current-time');
const totalTimeSpan = document.querySelector('.total-time');
const songTitleSpan = document.querySelector('.song-title');
const artistNameSpan = document.querySelector('.artist-name');
const musicAudio = document.querySelector('#music-audio');
const volumeControl = document.querySelector('#volume-control');
const likeButton = document.querySelector('.song-like-button');
const commentlikeButton = document.querySelector('.like-button');
const url = playPauseButton.getAttribute('data-url');
const comment_url = commentlikeButton.getAttribute('data-comment-url');
const commentId = commentlikeButton.getAttribute('data-comment-id');
const song_url = likeButton.getAttribute('data-url');
const songId = playPauseButton.getAttribute('data-song-id');

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift()
}


likeButton.addEventListener('click', () => {
        const csrftoken = getCookie('csrftoken')
        fetch(song_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: 'song_id=' + songId,
        })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error:', error))
});

let currentSongIndex = 0;

function loadSong() {
    const currentSong = songs[currentSongIndex]
    albumArtImage.src = currentSong.song_art.url
    songTitleSpan.textContent = currentSong.song_name
    artistNameSpan.textContent = currentSong.artist.display_name|safe
    musicAudio.src = currentSong.src
    musicAudio.play();
}

playPauseButton.addEventListener('click', () => {
    if (musicAudio.paused) {
        musicAudio.play();
        const csrftoken = getCookie('csrftoken')
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: 'song_id=' + songId,
        })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error:', error))
    } else {
        musicAudio.pause();
    }
});

commentlikeButton.addEventListener('click', () => {
        const csrftoken = getCookie('csrftoken')
        fetch(comment_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: 'comment_id=' + commentId,
        })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error:', error))
});

nextButton.addEventListener('click', () => {
    currentSongIndex = (currentSongIndex + 1 ) % songs.length;
    loadSong();
});

previousButton.addEventListener('click', () => {
    currentSongIndex = (currentSongIndex - 1 + songs.length)  % songs.length;
    loadSong();
});

musicAudio.addEventListener('timeupdate', () => {
    const progress = (musicAudio.currentTime / musicAudio.duration) * 100;
    progressBar.value = progress;
    currentTimeSpan.textContent = formatTime(musicAudio.currentTime);
    totalTimeSpan.textContent = formatTime(musicAudio.duration);
});

progressBar.addEventListener('input', () => {
    console.log(progressBar.value);
    musicAudio.currentTime = (progressBar.value / 100) * musicAudio.duration;
});

progressBar.addEventListener('change', () => {
    musicAudio.currentTime = (progressBar.value / 100) * musicAudio.duration;
});

volumeControl.addEventListener('input', () => {
    musicAudio.volume = volumeControl.value / 100;
});

function formatTime(time) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes.toString().padStart(2, `0`)}:${seconds.toString().padStart(2, `0`)}`;
}
loadSong();
