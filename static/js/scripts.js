document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('search');
  const watchList = document.getElementById('watch-list'); // Ensure this ID matches the container in your HTML

  // Function to display watches
  function displayWatches(watches, selectedCurrency) {
    watchList.innerHTML = ''; // Clear the current watch list

    if (watches && watches.length > 0) {
      watches.forEach(watch => {
        const watchElement = document.createElement('div');
        watchElement.classList.add('col', 'mb-5');
        watchElement.innerHTML = `
          <div class="card h-100">
            <img class="card-img-top" src="/image/${watch.id}" alt="..." width="100">
            <div class="card-body p-4">
              <div class="text-center">
                <h5 class="fw-bolder">${watch.brand} ${watch.name}</h5>
                ${selectedCurrency} ${watch.price.toFixed(2)}
              </div>
            </div>
            <div class="card-footer p-4 pt-0 border-top-0 bg-transparent">
              <div class="text-center">
                <a class="btn btn-outline-dark mt-auto" href="/view_watch/${watch.id}">View</a>
              </div>
            </div>
          </div>
        `;
        watchList.appendChild(watchElement);
      });
    } else {
      // If no watches are found, display a "no results" message
      const noResultsMessage = document.createElement('div');
      noResultsMessage.classList.add('col', 'mb-5');
      noResultsMessage.innerHTML = '<p>No watches found. Try a different search.</p>';
      watchList.appendChild(noResultsMessage);
    }
  }

  // Fetch and display all watches on initial page load
  fetch('/get_all_watches')
    .then(response => response.json())
    .then(data => {
      displayWatches(data.watches, data.selected_currency);
    })
    .catch(error => {
      console.error('Error fetching all watches:', error);
    });

  // Function to handle the search logic
  function searchWatches() {
    const searchQuery = this.value;

    // Fetch filtered watches based on the search query
    fetch(`/search_watches?query=${searchQuery}`)
      .then(response => response.json())
      .then(data => {
        displayWatches(data.watches, data.selected_currency);
      })
      .catch(error => {
        console.error('Error fetching search results:', error);
      });
  }

  // Attach the search function when typing in the input field
  if (searchInput) {
    searchInput.addEventListener('input', searchWatches);
  }
});
