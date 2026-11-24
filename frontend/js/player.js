let activePlayerInstance = null;

async function checkApiHealth() {
    const statusEl = document.getElementById("apiStatus");
    try {
        const res = await fetch("/health");
        if (res.ok) {
            statusEl.textContent = "سرور متصل است";
            statusEl.style.color = "#4ade80";
        } else {
            statusEl.textContent = "خطا در سرور";
            statusEl.style.color = "#f87171";
        }
    } catch (err) {
        statusEl.textContent = "قطع ارتباط با سرور";
        statusEl.style.color = "#f87171";
    }
}

function getSourceMimeType(urlText) {
    const lowerUrl = urlText.toLowerCase();
    if (lowerUrl.indexOf(".m3u8") !== -1) {
        return "application/x-mpegURL";
    }
    return "video/mp4";
}

function setupVideoPlayer(streamUrl) {
    if (activePlayerInstance !== null) {
        try {
            activePlayerInstance.destroy();
        } catch (err) {
            console.log("player destroy warning:", err);
        }
        activePlayerInstance = null;
    }

    const container = document.getElementById("playerContainer");
    container.innerHTML = "";

    const videoEl = document.createElement("video");
    videoEl.id = "mainVideoPlayer";
    videoEl.setAttribute("controls", "true");
    videoEl.setAttribute("playsinline", "true");

    const sourceEl = document.createElement("source");
    sourceEl.src = streamUrl;
    sourceEl.type = getSourceMimeType(streamUrl);

    videoEl.appendChild(sourceEl);
    container.appendChild(videoEl);

    if (typeof fluidPlayer === "function") {
        activePlayerInstance = fluidPlayer("mainVideoPlayer", {
            layoutControls: {
                fillToContainer: true,
                autoPlay: false,
                mute: false
            },
            vastOptions: {
                adList: [
                    {
                        roll: "preRoll",
                        vastTag: "/ads/vast.xml"
                    }
                ]
            }
        });
    }
}

async function openVideoBySlug(slugValue) {
    try {
        const response = await fetch("/videos/" + encodeURIComponent(slugValue));
        if (!response.ok) {
            return;
        }

        const videoData = await response.json();

        document.getElementById("videoTitle").textContent = videoData.title;
        document.getElementById("videoViews").textContent = "بازدید: " + videoData.views_count;
        document.getElementById("videoDuration").textContent = "مدت: " + videoData.duration_seconds + " ثانیه";

        if (videoData.description) {
            document.getElementById("videoDescription").textContent = videoData.description;
        } else {
            document.getElementById("videoDescription").textContent = "توضیحاتی ثبت نشده است.";
        }

        setupVideoPlayer(videoData.stream_url);
    } catch (err) {
        console.log("failed to load video:", err);
    }
}

async function loadVideoList() {
    const listContainer = document.getElementById("videoList");

    try {
        const response = await fetch("/videos/");
        if (!response.ok) {
            listContainer.innerHTML = "<p class='empty-msg'>خطا در دریافت لیست ویدیوها</p>";
            return;
        }

        const videos = await response.json();
        listContainer.innerHTML = "";

        if (videos.length === 0) {
            listContainer.innerHTML = "<p class='empty-msg'>هنوز هیچ ویدیویی ثبت نشده است.</p>";
            return;
        }

        for (let i = 0; i < videos.length; i++) {
            const item = videos[i];

            const card = document.createElement("div");
            card.className = "video-card";

            const titleDiv = document.createElement("div");
            titleDiv.className = "video-card-title";
            titleDiv.textContent = item.title;

            const subDiv = document.createElement("div");
            subDiv.className = "video-card-sub";
            subDiv.textContent = "بازدید: " + item.views_count + " | مدت: " + item.duration_seconds + " ثانیه";

            card.appendChild(titleDiv);
            card.appendChild(subDiv);

            card.addEventListener("click", function () {
                openVideoBySlug(item.slug);
            });

            listContainer.appendChild(card);
        }

        openVideoBySlug(videos[0].slug);
    } catch (err) {
        listContainer.innerHTML = "<p class='empty-msg'>عدم دسترسی به API</p>";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    checkApiHealth();
    loadVideoList();
});