import React, { useEffect, useState } from "react";
export default function Testpy() {
    
  const [html, setHTML] = useState({__html: ""});

  useEffect(() => {
    async function createMarkup() {
      let response;
      response = await fetch(`http://localhost:5000/trajet`)
       const backendHtmlString = await response.text()

       console.log(backendHtmlString)
        return {__html: backendHtmlString};
     }
     createMarkup().then(result => setHTML(result));
  }, []);
  

  return <div dangerouslySetInnerHTML={html} />;
}