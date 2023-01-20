import { Bar,Pie,Radar } from "react-chartjs-2";
import { Chart, registerables } from 'chart.js';


export default function Maison({ context, prixData, adresseLabel,villeData,prixM,prixData2022 }) {
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
            <div className="w-[900px] h-[900px]">
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
                      },{
                        label: 'prix Dataset 2022',
                        data: prixData2022,
                        fill: true,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgb(54, 162, 235)',
                        pointBackgroundColor: 'rgb(54, 162, 235)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(54, 162, 235)'
                      }
                    ]
                    }  }
                    />
                    
            
             </div>
            
      </>
    )
}
  
export async function getServerSideProps(ctx) {
    const { ville } = ctx.query;
    console.log(ville)
    const response = await fetch(`https://data.economie.gouv.fr/api/records/1.0/search/?dataset=prix-carburants-fichier-instantane-test-ods-copie&q=&facet=id&facet=adresse&facet=ville&facet=prix_maj&facet=prix_nom&facet=com_arm_name&facet=epci_name&facet=dep_name&facet=reg_name&facet=services_service&facet=horaires_automate_24_24&refine.prix_maj=2023%2F01&refine.ville=${ville}&exclude.prix_nom=E85&exclude.prix_nom=GPLc`)
    const response2 = await fetch(`https://data.economie.gouv.fr/api/records/1.0/search/?dataset=prix-carburants-fichier-instantane-test-ods-copie&q=&facet=id&facet=adresse&facet=ville&facet=prix_maj&facet=prix_nom&facet=com_arm_name&facet=epci_name&facet=dep_name&facet=reg_name&facet=services_service&facet=horaires_automate_24_24&refine.prix_maj=2022&refine.ville=${ville}`)
    const data = await response;
    const data1 = await response2;
    const json = await data.json();
    const json1 = await data1.json();
    const dataSet = [];
    const dataSet1= [];
    const label = [];
    let prixMoyenne=0;

    // console.log(json.records)
    json.records.forEach(element => {
        dataSet.push(element.fields.prix_valeur)
        label.push(element.fields.adresse )
    });
    json1.records.forEach(element => {
      dataSet1.push(element.fields.prix_valeur)
  });
    dataSet.forEach(prix => {
      prixMoyenne +=prix;
    })
    prixMoyenne=Math.round((prixMoyenne/dataSet.length)*100)/100;
    //console.log(dataSet);
    console.log(dataSet1)
    return {
        props: {
            villeData:ville,
            prixData: dataSet,
            prixData2022: dataSet1,
            adresseLabel: label,
            prixM: prixMoyenne
        }
    }
}