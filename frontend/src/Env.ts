export const SERVER_URL = window.location.hostname; //"192.168.0.104";
// export const SERVER_URL = "wordgame.space";
export const IO_PORT =
  process.env.NODE_ENV === "production" ? window.location.port : 5000;
// export const BASE_URL = "";
console.log("hostname:" + window.location.hostname);
console.log("port:" + window.location.port);

export const BASE_URL = "http://" + SERVER_URL + ":" + IO_PORT;
