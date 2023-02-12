import React, { useState } from 'react';
import axios from 'axios';

const TripForm = () => {
  const [date, setDate] = useState('');
  const [currentPosition, setCurrentPosition] = useState('');
  const [destination, setDestination] = useState('');
  const [html, setHTML] = useState({__html: ""});
  const [distance, setDistance] = useState('');
  const [prixPrevision, setPrix] = useState('');
  const [prixTotal, setTotal] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await axios.post('http://localhost:5000/trajet_map', {   
        currentPosition,
        destination
    });
    console.log(typeof(response.data))
    const backendHtmlString = await response.data
    //const distance = await response.data.distance
    setHTML({__html: backendHtmlString})
   // setDistance(distance)
   const responseDis = await axios.post('http://localhost:5000/distance', {   
    date,
    currentPosition,
    destination
    });
    console.log(responseDis.data)
    const distance = await responseDis.data.distance
    const prixPrevision = await responseDis.data.prixPrevision
    const prixTotal = await responseDis.data.prixTotal
    setDistance(distance)
    setPrix(prixPrevision)
    setTotal(prixTotal)
  };

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="date">Date:</label>
      <input
        type="date"
        id="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
        className='px-2'
      />

      <label htmlFor="current-position">Current Position:</label>
      <input
        type="text"
        id="current-position"
        value={currentPosition}
        onChange={(e) => setCurrentPosition(e.target.value)}
        className='px-2'
      />

      <label htmlFor="destination">Destination:</label>
      <input
        type="text"
        id="destination"
        value={destination}
        onChange={(e) => setDestination(e.target.value)}
        className='px-2'
      />

      <button className='inline-flex items-center px-3 py-2 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800' type="submit">Submit</button>
      {distance && (
        <div>
        <p>Distance: {distance}km</p>
        </div>

      )}
        {prixPrevision && (
        <p>Prix Gazole estimé: {prixPrevision}€</p>
      )}
        {prixTotal && (
        <><p>Prix Total estimé: {prixTotal}€</p></>
      )}
      {html && (
        <div dangerouslySetInnerHTML={html} />
      )}
    </form>
   
  );
};

export default TripForm;
