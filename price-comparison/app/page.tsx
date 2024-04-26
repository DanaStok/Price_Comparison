'use client';
import React, { useState } from 'react';

function Search() {
  const [productName, setProductName] = useState('');
  const [searchResults, setSearchResults] = useState([]); // State to store search results

  const handleSearch = async (e) => {
    e.preventDefault(); // Prevent the default form submit action
    try {
      const response = await fetch('http://127.0.0.1:8000/search/' + productName, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      console.log('Response data from the backend:', data);

      // Prepare an array of results for the table including URLs
      const results = [
        { company: 'BestBuy', productName: data.BestBuy.Item, price: data.BestBuy.Price, url: data.BestBuy.URL},
        { company: 'Walmart', productName: data.Walmart.Item, price: data.Walmart.Price, url: data.Walmart.URL},
        { company: 'Newegg', productName: data.Newegg.Item, price: data.Newegg.Price,  url: data.Newegg.URL}
      ];
      setSearchResults(results); // Update the state with the new results

    } catch (error) {
      console.error('There was an error!', error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          placeholder="Enter a product name"
        />
        <button type="submit">Search</button>
      </form>
      {searchResults.length > 0 && (
        <table className='table table-bordered'>
          <thead>
            <tr>
              <th>Company</th>
              <th>Product Name</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            {searchResults.map((result, index) => (
              <tr key={index}>
                <td>{result.company}</td>
                <td><a href={result.url} target="_blank" rel="noopener noreferrer">{result.productName}</a></td>
                <td>${result.price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Search;