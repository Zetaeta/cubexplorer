import {
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import axios from "axios";
import { useEffect, useState } from "react";

function CorrelationDisplay(props: { cardId: string }) {
  const cardId = props.cardId;
  const [data, setData] = useState({} as any);
  useEffect(() => {
    console.log("useEffect: ");
    console.log(cardId);
    if (cardId) {
      console.log("fetching");
      axios.get("http://localhost:5000/api/cov/" + cardId).then((response) => {
        console.log(response);
        setData(response.data);
      });
    } else {
      setData({});
    }
  }, [cardId]);
  if (!data?.top) {
    return null;
  }
  return (
    <div>
      <Stack spacing={2}>
        <div>
          Most correlated cards{" "}
          <CorrelationTable entries={data.top}></CorrelationTable>
        </div>
        <div>
          Least correlated cards{" "}
          <CorrelationTable entries={data.bottom}></CorrelationTable>
        </div>
      </Stack>
    </div>
  );
}

function CorrelationTable(props: { entries: any[] }) {
  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }}>
        <TableHead>
          <TableRow>
            <TableCell align="left">Card</TableCell>
            <TableCell align="right">Correlation</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {props.entries.map((entry: any, j) => {
            return (
              <TableRow key={j}>
                <TableCell align="left">{entry.card_name}</TableCell>
                <TableCell align="right">{entry.corr.toFixed(2)}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default CorrelationDisplay;
