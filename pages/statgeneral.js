import {Ps} from 'pyscript-js'

function StatGeneral(){
    return(
        <>
        <h1 className="text-3xl font-bold underline text-red-500">
        Stat General
            </h1>
            <Ps>
                import pandas as pd
                es = pd.read_csv('/content/drive/My Drive/data/essence.csv', sep=';')
                es = es.drop(columns=['id','horaires', 'prix_id', 'services_service', 'horaires_automate_24_24', 'epci_code', 'epci_name', 'reg_code', 'com_name', 'com_code'], axis=1)   
                print(es.shape)
                print(es.dtypes)
                list(es)
                print(es.head())
            </Ps>
        </>
    )
}

export default StatGeneral;