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
                        label: 'prix Gasoil 2023',
                        data: prixData,
                        fill: true,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgb(255, 99, 132)',
                        pointBackgroundColor: 'rgb(255, 99, 132)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgb(255, 99, 132)'
                      },{
                        label: 'prix Gasoil 2022',
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
    const response = await fetch(`https://public.opendatasoft.com/api/records/1.0/search/?dataset=prix_des_carburants_j_7&q=&facet=cp&facet=pop&facet=city&facet=automate_24_24&facet=fuel&facet=shortage&facet=update&facet=services&facet=brand&refine.fuel=Gazole&refine.city=${ville}&refine.update=2023`)
    const response2 = await fetch(`https://public.opendatasoft.com/api/records/1.0/search/?dataset=prix_des_carburants_j_7&q=&facet=cp&facet=pop&facet=city&facet=automate_24_24&facet=fuel&facet=shortage&facet=update&facet=services&facet=brand&refine.update=2022&refine.fuel=Gazole&refine.city=${ville}`)
    const data = await response;
    const data1 = await response2;
    const json = await data.json();
    const json1 = await data1.json();
    const dataSet = [];
    const dataSet1= [];
    const label = [];
    let prixMoyenne=0;

     console.log(json.records)
    json.records.forEach(element => {
        dataSet.push(element.fields.price_gazole*1000)
        
        label.push(element.fields.address )
        
    });
    json1.records.forEach(element => {
      dataSet1.push(element.fields.price_gazole*1000)
  });
    dataSet.forEach(prix => {
      prixMoyenne +=prix;
    })
    prixMoyenne=Math.round((prixMoyenne/dataSet.length)*100)/100;
    //console.log(dataSet);
    console.log(dataSet)
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