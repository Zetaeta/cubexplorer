import Grid from "@mui/material/Grid";
import { useLoaderData } from "react-router-dom";

function CardPage() {
  const cards = useLoaderData() as any[];
  return (
    <div>
      <Grid container spacing={1}>
        {cards.map((card: any) => {
          return (
            <Grid item>
              <a href={"/cards/" + card.id}>
                <img src={card.image} alt={card.name}></img>
              </a>
            </Grid>
          );
        })}
      </Grid>
    </div>
  );
}

export default CardPage;
