import { useRef } from "react";
import {useRouter} from 'next/router'
import React, { useState } from 'react';
import { Input } from "postcss";
const SearchBar = () => {
    const router = useRouter()
    let [InputValue, setValue] = useState("");
    let handleValue = (event)=>{
       setValue(event.target.value)
    }
    const handleClick = async () =>{
        if(InputValue&&(InputValue.replace(/(^s*)|(s*$)/g," ").length !=0)){
            InputValue = InputValue.toUpperCase();
            let url = `/maison?ville=${InputValue}`;
            router.push(url)
        }
        else{
            alert("Mot clé ne peut pas être vide!")
        }
    }

    // CSS in header.css
    return (
        <div className="absolute flex justify center items-center left-6 px-4">
            <div className="relative mr-1 ">
            
                <input
                    type="text"
                    className="block p-2 w-40 h-7 text-gray-900 bg-gray-50 rounded"
                    name='name'
                    placeholder="Recherche..."
                    value = {InputValue}
                    onChange={handleValue}
                />
            </div>
            <div className="relative mr-3">
                <button
                    onClick={handleClick}
                    className="block w-10 h-7 text-blue-700 text-sm bg-gray-50"
                >
                    Ok
                </button>
            </div>
        </div>
    );
}

export default SearchBar


