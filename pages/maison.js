import { Bar } from "react-chartjs-2";
import { Chart, registerables } from 'chart.js';


import { useState } from "react";

export default function Maison({ context, prixData, adresseLabel }) {
    Chart.register(...registerables);
    const labels = ["January", "February", "March", "April", "May", "June"];
    const data = {
      labels: adresseLabel,
      datasets: [
        {
          label: "Prix du carburant",
          backgroundColor: "rgb(255, 99, 132)",
          borderColor: "rgb(255, 99, 132)",
          data: prixData    ,
        },
      ],
    };
    return (
      <>
        <h1 className="text-3xl font-bold underline text-red-500">
        MAison
            </h1>
            <div className="w-[1200px] h-[1200px]">
            <Bar data={data} />

            </div>
      </>
    )
}
  
export async function getServerSideProps(ctx) {
    const { ville } = ctx.query;
    console.log(ville)
    const response = await fetch(`https://data.economie.gouv.fr/api/records/1.0/search/?dataset=prix-carburants-fichier-instantane-test-ods-copie&q=prix_nom%3AGazole+OR+prix_nom%3AE10&facet=id&facet=ville&facet=prix_maj&facet=prix_nom&facet=com_arm_name&facet=epci_name&facet=dep_name&facet=reg_name&refine.prix_maj=2023%2F01&refine.prix_nom=Gazole&refine.ville=${ville}`)
    const data = await response;
    const json = await data.json();

    const dataSet = [];
    const label = [];

    // console.log(json.records)
    json.records.forEach(element => {
        dataSet.push(element.fields.prix_valeur)
        label.push(element.fields.adresse )
    });
    console.log(dataSet);
    return {
        props: {
            prixData: dataSet,
            adresseLabel: label
        }
    }
}