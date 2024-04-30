'use client';
import React, { useState, FormEvent } from 'react';
import "./layout.css";
import "./types.ts"
import "./title.css"

function Search() {
  const [productName, setProductName] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]); // State to SearchResult items
  const [isLoading, setIsLoading] = useState(false);
  const [cart, setCart] = useState<SearchResult[]>([]); // State to SearchResult items
  const [total, setTotal] = useState(0); // State to store total price

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/search/' + productName);
      const data = await response.json();
      console.log('Received data:', data);
      const results: SearchResult[] = [
        { company: 'BestBuy', productName: data.BestBuy?.Item ?? '', price: data.BestBuy?.Price?.toString() ?? '', url: data.BestBuy?.URL ?? '' },
        { company: 'Newegg', productName: data.Newegg?.Item ?? '', price: data.Newegg?.Price?.toString() ?? '', url: data.Newegg?.URL ?? '' },
        { company: 'Walmart', productName: data.Walmart?.Item ?? '', price: data.Walmart?.Price?.toString() ?? '', url: data.Walmart?.URL ?? '' }
      ];
      setSearchResults(results);
    } catch (error) {
      console.error('There was an error!', error);
    }
    setIsLoading(false);
  };

  const addToList = (item: SearchResult) => {
    setCart(current => [...current, item]);
    setTotal(currentTotal => {
      const itemPrice = isNaN(Number(item.price)) ? 0 : Number(item.price);
      const updatedTotal = currentTotal + itemPrice;
      return parseFloat(updatedTotal.toFixed(2));
    });
  };

  const clearCart = () => {
    setCart([]);
    setTotal(0);
  };
  

  return (
    <div>
      <h1 className="title">Price Comparator</h1> 
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          placeholder="Enter a product name"
          className="input input-bordered input-secondary w-full max-w-xs"
          style={{ marginRight: '8px'}}
        />
        <button className="btn">Search</button>
      </form>
      {isLoading && (
        <div className="spinner-container">
          <span className="loading loading-ring loading-lg"></span>
        </div>
      )}
      {searchResults.length > 0 && (
      <>
        <div className="table-container">
          <table className='table table-bordered'>
            <thead>
              <tr>
                <th>Company</th>
                <th>Product Name</th>
                <th>Price</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {searchResults.map((result, index) => (
                <tr className="hover" key={index}>
                  <td>{result.company}</td>
                  <td>
                    <a href={result.url} target="_blank" rel="noopener noreferrer" className="link link-hover">
                      {result.productName}
                    </a>
                  </td>
                  <td>${Number(result.price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                  <td>
                    <button className="btn btn-accent" onClick={() => addToList(result)}>
                      + 
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </>
      )}
      <div className="wishlist-container">
        <button className="btn top-right-btn"  
        onClick={() => {
          const modal = document.getElementById('my_modal_3') as HTMLDialogElement;
          modal?.showModal();
        }}
        >
          Wish List
        </button>
        <dialog id="my_modal_3" className="modal">
          <div className="modal-box">
            <form method="dialog">
              <button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
            </form>
            <h3 className="font-bold text-lg">Wish List</h3>
            {cart.length === 0 && (
              <h4>No Items Selected</h4>
            )}
            {cart.length > 0 && (
              <>
              <ul className="my-list">
                {cart.map((item, index) => (
                  <li key={index}>{item.productName} - ${item.price}</li>
                ))}
              </ul>
              <h4 className="font-bold text-lg">Total: ${total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</h4>
              <button className="btn btn-error" onClick={clearCart}>
                Clear Cart
              </button>
              </>
            )}
          </div>
        </dialog>
      </div>
      </div> 
  );
}

export default Search;
