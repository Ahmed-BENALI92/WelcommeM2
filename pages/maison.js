import { Bar,Pie,Radar } from "react-chartjs-2";
import { Chart, registerables } from 'chart.js';


export default function Maison({ context, prixData, adresseLabel,villeData,prixM }) {
    Chart.register(...registerables);
    const data = {
      labels: adresseLabel,
      datasets: [
        {
          label: "Prix du carburant",
          backgroundColor: ["rgb(255, 99, 132)"],
          //backgroundColor: ["rgb(255, 99, 132)","#15ea4e","#15e6ea","#2a10ef","#a90ef1","#f5130a","#d2ee11","#000dff","#fd02a7","#ff7e00","#0d0600","#93629d"],
          borderColor: "rgb(255, 99, 132)",
          data: prixData    ,
        },
      ],
    };
    return (
      <>
        <h1 className="text-3xl font-bold underline text-red-500">
        Stat Pour la Ville de {villeData}
            </h1>
            <p>Le prix moyenne de la villes est de : {prixM}€/L</p>
            <div className="w-[1200px] h-[1200px]">
            <Bar data={data} />
            <Radar
                datasetIdKey='id'
                data={{
                    labels: adresseLabel,
                      datasets: [{
                        label: 'prix Dataset',
                        data: prixData,
                        fill: true,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgb(255, 99, 132)',
                        pointBackgroundColor: 'rgb(255, 99, 132)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(255, 99, 132)'
                      }]
                    }  }
                    />
            
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
    let prixMoyenne=0;

    // console.log(json.records)
    json.records.forEach(element => {
        dataSet.push(element.fields.prix_valeur)
        label.push(element.fields.adresse )
    });
    dataSet.forEach(prix => {
      prixMoyenne +=prix;
    })
    prixMoyenne=Math.round((prixMoyenne/dataSet.length)*100)/100;
    //console.log(dataSet);
    return {
        props: {
            villeData:ville,
            prixData: dataSet,
            adresseLabel: label,
            prixM: prixMoyenne
        }
    }
}