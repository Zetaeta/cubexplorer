import React, { useEffect, useState } from "react";
import axios from "axios";
// import logo from './logo.svg';
import "./App.css";
import Button from "@mui/material/Button";

function App() {
  const [getMessage, setGetMessage] = useState<any>({});

  useEffect(() => {
    axios
      .post("http://localhost:5000/tree", { path: [] })
      .then((response) => {
        console.log("SUCCESS", response);
        setGetMessage(response);
      })
      .catch((error) => {
        console.log(error);
      });
  }, []);
  return (
    <div className="App">
      <header className="App-header">
        <div>
          {getMessage.status === 200 ? (
            getMessage.data.type === "node" ? (
              <CardChoice
                message={getMessage.data}
                setMessage={setGetMessage}
              ></CardChoice>
            ) : (
              <h3>
                Your cube is:{" "}
                <a
                  href={
                    "https://cubecobra.com/cube/overview/" +
                    getMessage.data.cube
                  }
                >
                  {getMessage.data.cube}
                </a>
              </h3>
            )
          ) : (
            <h3>LOADING</h3>
          )}
        </div>
      </header>
    </div>
  );
}

function CardChoice(props: any) {
  const message = props.message;
  const condition = message.condition;
  const card = condition.card;
  function makeChoice(value: boolean) {
    axios
      .post("http://localhost:5000/tree", {
        path: [
          ...message.path,
          {
            card: condition.card.oracle_id,
            comp: value ? ">" : "<=",
          },
        ],
      })
      .then((response) => {
        console.log(response);
        props.setMessage(response);
        const newCard = response.data.condition.card;
        axios
          .get("http://localhost:5000/api/cov/" + newCard.oracle_id)
          .then((response) => {
            console.log(response);
          });
      });
  }
  return (
    <div>
      <a href={card.url}>
        <img src={card.normal} alt={card.name}></img>
      </a>
      <div>
        Include {message.cut} or more copies of {card.name}?
      </div>
      <div>
        <Button
          variant="contained"
          onClick={() => {
            makeChoice(true);
          }}
        >
          Yes
        </Button>
        <Button
          variant="contained"
          color="error"
          onClick={() => {
            makeChoice(false);
          }}
        >
          No
        </Button>
      </div>
      <h3>{JSON.stringify(message)}</h3>
    </div>
  );
}

export default App;
