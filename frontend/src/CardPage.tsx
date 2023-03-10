import { useLoaderData } from "react-router-dom";

function CardPage() {
  const card = useLoaderData() as any;
  return (
    <div>
      <img src={card.image_normal} alt={card.name}></img>
    </div>
  );
}

export default CardPage;
