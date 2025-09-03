// API Base URL - Update this to match your backend
const API_BASE_URL = 'http://localhost:5000';

function setupCreatePostButtonListener() {
    const createPostBtn = document.getElementById('createPostBtn');
    if (createPostBtn) {
        createPostBtn.addEventListener('click', () => {
            const modal = document.getElementById('createPostForm');
            if (modal) {
                modal.style.display = 'block';
            }
        });
    }
}

// Authentication check - redirect to login if not authenticated
function checkAuthentication() {
    const token = localStorage.getItem('authToken');
    const userName = localStorage.getItem('userName');
    
    if (!token || !userName) {
        // Not authenticated, redirect to login
        window.location.href = 'login.htm';
        return false;
    }
    return true;
}

// Check authentication when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check for OAuth callback parameters first
    if (handleOAuthCallback()) {
        return; // OAuth callback handled, authentication will be checked next
    }
    
    if (!checkAuthentication()) {
        return;
    }
    
    // Initialize the page with authenticated user data
    initializeAuthenticatedUser();
});

// Handle OAuth callback parameters
function handleOAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const isNewUser = urlParams.get('is_new_user') === 'true';
    const userId = urlParams.get('user_id');
    const userType = urlParams.get('user_type');
    
    if (token && userId && userType) {
        // Store authentication data
        localStorage.setItem('authToken', token);
        localStorage.setItem('userId', userId);
        localStorage.setItem('userType', userType);
        
        // Get additional user info from token (decode JWT)
        try {
            const tokenPayload = JSON.parse(atob(token.split('.')[1]));
            
            // Store user info from token
            localStorage.setItem('userName', 'Google User'); // Will be updated when we fetch user data
            localStorage.setItem('userEmail', 'oauth@google.com'); // Will be updated when we fetch user data
            
            // Clear URL parameters
            window.history.replaceState({}, document.title, window.location.pathname);
            
            // Show welcome message for new users
            if (isNewUser) {
                alert('Welcome to FarmLink! Please complete your profile.');
            }
            
            // Initialize the page
            initializeAuthenticatedUser();
            return true;
            
        } catch (error) {
            console.error('Error processing OAuth token:', error);
            // Clear invalid token
            localStorage.removeItem('authToken');
            return false;
        }
    }
    
    return false;
}

// Initialize authenticated user data
async function initializeAuthenticatedUser() {
    const userName = localStorage.getItem('userName');
    const userEmail = localStorage.getItem('userEmail');
    const userType = localStorage.getItem('userType');
    
    // If this is an OAuth user with placeholder data, fetch real user info
    if (userName === 'Google User' || userEmail === 'oauth@google.com') {
        await fetchUserInfoFromBackend();
    } else {
        // Update UI with existing user info
        updateUserInfoInUI(userName, userEmail);
    }
    
    // Load marketplace posts from API
    await loadMarketplacePosts();
    // displayMarketplacePosts was removed; use displayPosts
    await displayPosts();
    await displayUserPosts();
}

// Fetch user info from backend for OAuth users
async function fetchUserInfoFromBackend() {
    try {
        const token = localStorage.getItem('authToken');
        const userId = localStorage.getItem('userId');
        
        if (!token || !userId) {
            console.error('No token or user ID available');
            return;
        }
        
        // Call backend to get user info
        const response = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            
            // Update localStorage with real user data
            localStorage.setItem('userName', userData.name || 'Google User');
            localStorage.setItem('userEmail', userData.email || 'oauth@google.com');
            localStorage.setItem('userContact', userData.mobile || '');
            
            // Update UI
            updateUserInfoInUI(userData.name, userData.email);
        } else {
            console.error('Failed to fetch user info:', response.statusText);
            // Use placeholder data
            updateUserInfoInUI('Google User', 'oauth@google.com');
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
        // Use placeholder data
        updateUserInfoInUI('Google User', 'oauth@google.com');
    }
}

// Update user info in UI
function updateUserInfoInUI(userName, userEmail) {
    if (profileNameNavSpan) profileNameNavSpan.textContent = userName;
    if (dropdownProfileNameSpan) dropdownProfileNameSpan.textContent = userName;
    if (dropdownProfileEmailSpan) dropdownProfileEmailSpan.textContent = userEmail;
}

// Load marketplace posts from API
async function loadMarketplacePosts(userTypeFilter = null, authorIdFilter = null) {
    try {
        const token = getAuthToken(); // Get the authentication token
        
        // Include Authorization header if a token exists
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        let url = `${API_BASE_URL}/api/posts`;
        const params = new URLSearchParams();

        if (userTypeFilter) {
            params.append('user_type', userTypeFilter);
        }
        if (authorIdFilter) {
            params.append('author_id', authorIdFilter);
        }

        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        const response = await fetch(url, {
            headers: headers
        });
        const data = await response.json();
        
        if (response.ok) {
            // Update the marketplacePosts array with API data
            marketplacePosts = data.posts || [];
            
            // Refresh the UI. No longer calling displayPosts or displayUserPosts directly
            // as the calling functions will handle which display function is needed.
        } else {
            console.error('Failed to load posts:', data.error);
            marketplacePosts = []; // Clear posts if loading fails
        }
    } catch (error) {
        console.error('Error loading posts:', error);
        marketplacePosts = []; // Clear posts on network error
    }
}

// Store data in localStorage
let marketplacePosts = []; // Initialize as empty, will be populated by API
let userChats = JSON.parse(localStorage.getItem('userChats')) || {};
let userProfiles = JSON.parse(localStorage.getItem('userProfiles')) || {};
let postViews = JSON.parse(localStorage.getItem('postViews')) || {};
let postRatings = JSON.parse(localStorage.getItem('postRatings')) || {};

// Get elements for the static navigation bar and content sections
let navMarketplace = document.getElementById('navMarketplace');
let navMyPosts = document.getElementById('navMyPosts');
let navChats = document.getElementById('navChats');
// navEditProfile is removed from HTML, so we don't need to get it here
// let navEditProfile = document.getElementById('navEditProfile');

// New Navbar Logout Button
const navBarLogoutBtn = document.getElementById('navBarLogoutBtn'); // Get the new logout button

// Profile Access System Dropdown elements
const profileDropdownTrigger = document.getElementById('profileDropdownTrigger');
const profileDropdownContent = document.getElementById('profileDropdownContent');
const profileNameNavSpan = document.getElementById('profileNameNav');
const dropdownProfileNameSpan = document.getElementById('dropdownProfileName');
const dropdownProfileEmailSpan = document.getElementById('dropdownProfileEmail');
const dropdownEditProfileLink = document.getElementById('dropdownEditProfile');
const dropdownLogoutLink = document.getElementById('dropdownLogout');

// Content sections
let marketplaceSection = document.getElementById('marketplaceSection');
let myPostsSection = document.getElementById('myPostsSection');
let chatsSection = document.getElementById('chatsSection');
let editProfileSection = document.getElementById('editProfileSection');
let dashboardSection = document.getElementById('dashboardSection');

// Containers within sections
const buyerPostsContainer = document.getElementById('buyerPosts');
const farmerPostsContainer = document.getElementById('farmerPosts');
const userPostsContainer = document.getElementById('userPostsContainer');

// Chat elements (updated IDs based on new HTML structure)
const chatListPanel = document.querySelector('.chat-list-panel');
const chatWindowPanel = document.getElementById('activeChatWindow');
const chatSearchInput = document.getElementById('chatSearchInput');
const conversationList = document.getElementById('conversationList');
const activeChatHeader = document.getElementById('activeChatHeader');
const chatMessagesContainer = document.getElementById('activeChatWindow') ? document.getElementById('activeChatWindow').querySelector('#chatMessages') : document.getElementById('chatMessages');
let chatInput = document.getElementById('activeChatWindow') ? document.getElementById('activeChatWindow').querySelector('#chatInput') : document.getElementById('chatInput');
let sendMessageBtn = document.getElementById('activeChatWindow') ? document.getElementById('activeChatWindow').querySelector('#sendMessage') : document.getElementById('sendMessage');
const closeChatPanelBtn = chatWindowPanel ? chatWindowPanel.querySelector('.close-chat-panel') : null;

// Edit Profile elements
const profileEditForm = document.getElementById('profileEditForm');
const editUserNameInput = document.getElementById('editUserName');
const editUserContactInput = document.getElementById('editUserContact');
const saveProfileBtn = document.getElementById('saveProfileBtn');

// Post Creation Modal elements
const createPostModal = document.getElementById('createPostForm');
const closePostModalBtn = createPostModal ? createPostModal.querySelector('.close-btn') : null;
let createPostBtn = document.getElementById('createPostBtn');
let postCropBtn = document.getElementById('postCrop');
let postRequirementBtn = document.getElementById('postRequirement');


// --- Core Functions ---

function hideAllContentSections() {
    const sections = [dashboardSection, marketplaceSection, myPostsSection, chatsSection, editProfileSection];
    sections.forEach(section => {
        if (section) {
            section.style.display = 'none';
        }
    });
}

function showSection(sectionElement, navLinkId) {
    hideAllContentSections();
    if (sectionElement) {
        if (sectionElement === chatsSection) {
             sectionElement.style.display = 'flex';
             if (chatListPanel) chatListPanel.style.display = 'flex';
             if (chatWindowPanel) chatWindowPanel.classList.remove('active-chat');
        } else if (sectionElement === marketplaceSection) {
             sectionElement.style.display = 'block';
              const contentWrapper = marketplaceSection.querySelector('.content-wrapper');
              if(contentWrapper) contentWrapper.style.display = 'flex';
        } else if (sectionElement === dashboardSection) {
             sectionElement.style.display = 'block';
             populateDashboard();
        }
        else {
            sectionElement.style.display = 'block';
        }
        const mainContent = document.querySelector('main');
        if (mainContent) {
             mainContent.scrollTop = 0;
        }
    }
     if (navLinkId) {
         highlightActiveNav(navLinkId);
     }
}

function getCurrentUser() {
    return localStorage.getItem('userName');
}

function getCurrentUserId() {
    return localStorage.getItem('userId');
}

function getAuthToken() {
    return localStorage.getItem('authToken');
}

// Helper: fetch and cache a user's display name by id
async function fetchAndCacheUserName(userId) {
    try {
        if (!userId) return null;
        // If cached name exists, return it
        const cached = userProfiles[userId];
        if (cached && cached.name) return cached.name;

        const token = getAuthToken();
        if (!token) return null;

        const res = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return null;
        const data = await res.json();
        const name = data.name || data.username || 'User';

        userProfiles[userId] = { ...(userProfiles[userId] || {}), name: name, email: data.email };
        localStorage.setItem('userProfiles', JSON.stringify(userProfiles));
        return name;
    } catch (e) {
        return null;
    }
}

// Helper: fetch minimal public user data (no auth) and cache it
async function fetchAndCacheUserPublicName(userId) {
    try {
        if (!userId) return null;
        const cached = userProfiles[userId];
        if (cached && cached.name) return cached.name;

        const res = await fetch(`${API_BASE_URL}/api/users/${userId}/public`);
        if (!res.ok) return null;
        const data = await res.json();
        const name = data.name || 'User';
        userProfiles[userId] = { ...(userProfiles[userId] || {}), name: name };
        localStorage.setItem('userProfiles', JSON.stringify(userProfiles));
        return name;
    } catch {
        return null;
    }
}

function getCurrentUserType() {
     return window.location.pathname.includes('farmer.html') ? 'farmer' : 'buyer';
}

function highlightActiveNav(activeLinkId) {
    const navLinks = document.querySelectorAll('.main-nav ul a');
    navLinks.forEach(link => {
        if (link.id === activeLinkId) {
            link.classList.add('active-nav');
        } else {
            link.classList.remove('active-nav');
        }
    });
}


// --- Navigation Event Listeners ---

if (navMarketplace) {
    navMarketplace.addEventListener('click', (e) => {
        e.preventDefault();
        showSection(marketplaceSection, 'navMarketplace');
        displayPosts();
         if (profileDropdownContent) profileDropdownContent.classList.remove('show');
    });
}

if (navMyPosts) {
    navMyPosts.addEventListener('click', (e) => {
        e.preventDefault();
        showSection(myPostsSection, 'navMyPosts');
        displayUserPosts();
         if (profileDropdownContent) profileDropdownContent.classList.remove('show');
    });
}

if (navChats) {
    navChats.addEventListener('click', (e) => {
        e.preventDefault();
        showSection(chatsSection, 'navChats');
        displayConversationsList();
         if (profileDropdownContent) profileDropdownContent.classList.remove('show');
    });
}

// Removed the event listener for navEditProfile as it's no longer in HTML


// --- Profile Access System Dropdown Logic ---

if (profileDropdownTrigger && profileDropdownContent) {
    profileDropdownTrigger.addEventListener('click', (e) => {
        e.preventDefault();
        profileDropdownContent.classList.toggle('show');
         if (profileDropdownContent.classList.contains('show')) {
             populateProfileDropdown();
         }
    });

    window.addEventListener('click', (event) => {
        if (!profileDropdownTrigger.contains(event.target) && !profileDropdownContent.contains(event.target)) {
            if (profileDropdownContent.classList.contains('show')) {
                profileDropdownContent.classList.remove('show');
            }
        }
    });
}

function populateProfileDropdown() {
    const currentUser = getCurrentUser();
    if (!currentUser) {
        if (profileNameNavSpan) profileNameNavSpan.textContent = 'Guest';
        if (dropdownProfileNameSpan) dropdownProfileNameSpan.textContent = 'N/A';
        if (dropdownProfileEmailSpan) dropdownProfileEmailSpan.textContent = 'N/A';
        return;
    }

    const userProfile = userProfiles[currentUser] || { name: currentUser, email: 'N/A', userType: getCurrentUserType() };

    if (profileNameNavSpan) profileNameNavSpan.textContent = userProfile.name || currentUser;
    if (dropdownProfileNameSpan) dropdownProfileNameSpan.textContent = userProfile.name || currentUser;
    if (dropdownProfileEmailSpan) dropdownProfileEmailSpan.textContent = userProfile.email || 'N/A';
}


// Event listener for "Edit Profile" link in dropdown
if (dropdownEditProfileLink) {
    dropdownEditProfileLink.addEventListener('click', (e) => {
        e.preventDefault();
        showSection(editProfileSection, 'navEditProfile'); // This will still highlight if navEditProfile existed, but the section will show
        populateEditProfileForm();
         if (profileDropdownContent) profileDropdownContent.classList.remove('show');
    });
}

// Event listener for "Logout" link in dropdown
if (dropdownLogoutLink) {
    dropdownLogoutLink.addEventListener('click', (e) => {
      e.preventDefault();
      // Reusing the same logout logic for both logout buttons
      performLogout();
    });
}

// Event listener for the new Logout button in the navbar
if (navBarLogoutBtn) {
    navBarLogoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        performLogout();
    });
}

// Centralized Logout Function
function performLogout() {
     const confirmLogout = confirm('Are you sure you want to logout?');
      if (confirmLogout) {
        localStorage.removeItem('userName');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userType');
        localStorage.removeItem('userContact');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userId');
        localStorage.removeItem('currentUserType');
        window.location.href = 'login.htm';
      }
}


// --- Dashboard Content (Placeholder) ---
function populateDashboard() {
    const dashboardContentDiv = dashboardSection;
    if (dashboardContentDiv) {
        dashboardContentDiv.innerHTML = '<h3>Welcome to your Dashboard!</h3><p>This is where your activity summary and quick access items will appear.</p>';
    }
}


// --- Post Management ---

function createPostElement(post, isUserPost = false) {
  const postElement = document.createElement('div');
  postElement.className = 'post-card';
  
  let postContent = '';
  if (post.user_type === 'farmer') {
    postContent = `
      <h3>${post.crop_name}</h3>
      <p><strong>Details:</strong> ${post.crop_details}</p>
      <p><strong>Quantity:</strong> ${post.quantity}</p>
      <p><strong>Location:</strong> ${post.location}</p>
       <p><strong>Posted:</strong> ${new Date(post.created_at).toLocaleString()}</p>
    `;
  } else { // buyer post
    postContent = `
      <h3>${post.name}</h3>
      <p><strong>Organization:</strong> ${post.organization}</p>
      <p><strong>Location:</strong> ${post.location}</p>
      <p><strong>Requirements:</strong> ${post.requirements}</p>
       <p><strong>Posted:</strong> ${new Date(post.created_at).toLocaleString()}</p>
    `;
  }

  const postActions = document.createElement('div');
  postActions.className = 'post-actions';

  if (!isUserPost) {
      const chatBtn = document.createElement('button');
      chatBtn.className = 'chat-btn';
      const authorId = post.author_id;
      const authorProfile = userProfiles[authorId] || {};
      const initialDisplayName = authorProfile.name || authorId;

      chatBtn.textContent = `Chat with ${initialDisplayName}`;
      chatBtn.dataset.authorId = authorId;
       chatBtn.addEventListener('click', (e) => {
          e.preventDefault();
          const aId = chatBtn.dataset.authorId;
          if (aId) {
              openChat(getCurrentUserId(), aId);
              showSection(chatsSection, 'navChats');
               if (profileDropdownContent) profileDropdownContent.classList.remove('show');
          }
      });
      postActions.appendChild(chatBtn);

      // If we don't have the author's name cached yet, fetch from public endpoint and update the label
      if (!authorProfile.name) {
          fetchAndCacheUserPublicName(authorId).then((name) => {
              if (name && chatBtn && chatBtn.dataset.authorId === authorId) {
                  chatBtn.textContent = `Chat with ${name}`;
              }
          }).catch(() => {});
      }
  }

   // Only show edit/delete for the owner always
   const currentUserId = getCurrentUserId();
   const userOwnsPost = currentUserId && post.author_id === currentUserId;
   if (isUserPost || userOwnsPost) {
       const deleteBtn = document.createElement('button');
       deleteBtn.className = 'action-btn delete-btn';
       deleteBtn.innerHTML = '&#x1F5D1; Delete';
       deleteBtn.addEventListener('click', () => {
           if (confirm('Are you sure you want to delete this post?')) {
                deletePost(post.id);
           }
       });
       postActions.appendChild(deleteBtn);

       const editBtn = document.createElement('button');
       editBtn.className = 'action-btn edit-btn';
       editBtn.innerHTML = '&#x270E; Edit';
        editBtn.addEventListener('click', () => {
            openEditPostModal(post);
        });
       postActions.appendChild(editBtn);
   }


  postElement.innerHTML = postContent;
  postElement.appendChild(postActions);
  
  return postElement;
}

async function displayPosts(filteredPosts = null) {
  const isFarmerPage = getCurrentUserType() === 'farmer';
  const postsContainer = isFarmerPage ? buyerPostsContainer : farmerPostsContainer;
  const postTypeToDisplay = isFarmerPage ? 'buyer' : 'farmer';

  // If a filtered list is provided (e.g., from search), use it as-is and do not refetch
  let postsToDisplay = filteredPosts;
  if (!postsToDisplay) {
    // Otherwise fetch from backend with user type filter
    await loadMarketplacePosts(postTypeToDisplay);
    postsToDisplay = marketplacePosts;
  }

  
  if (postsContainer) {
    postsContainer.innerHTML = '';
    const relevantPosts = postsToDisplay.filter(post => {
        // The backend should already filter by user_type, but keep this for safety if data mixed
        return post && post.user_type && post.user_type === postTypeToDisplay;
    });

    if (relevantPosts.length > 0) {
        relevantPosts.forEach(post => {
            postsContainer.appendChild(createPostElement(post));
        });
    } else {
         postsContainer.innerHTML = `<p>No ${postTypeToDisplay} posts available yet.</p>`;
    }
  }
}

async function displayUserPosts() {
    const currentUser = getCurrentUser();
    const currentUserId = getCurrentUserId(); // Get the actual user ID

    if (!currentUserId) {
        console.error('User ID not available to display user posts.');
        return;
    }

    // Load posts (endpoint doesn't filter by author_id yet), then filter locally by owner
    await loadMarketplacePosts();
    const userPosts = (marketplacePosts || []).filter(post => post && post.author_id === currentUserId);

    if (userPostsContainer) {
        userPostsContainer.innerHTML = '';
        if (userPosts.length > 0) {
            userPosts.forEach(post => {
                 // Passing true to createPostElement adds the delete and edit buttons
                 userPostsContainer.appendChild(createPostElement(post, true));
            });
        } else {
            userPostsContainer.innerHTML = `<p>You haven't created any posts yet.</p>`;
        }
    }
}

if (createPostBtn) {
    createPostBtn.addEventListener('click', () => {
        if (createPostModal) {
            createPostModal.style.display = 'block';
            const formInputs = createPostModal.querySelectorAll('.form-input');
            formInputs.forEach(input => {
                if (input.type === 'text' || input.tagName === 'TEXTAREA' || input.type === 'number') {
                    input.value = '';
                } else if (input.tagName === 'SELECT') {
                    input.selectedIndex = 0;
                }
            });

             postCropBtn = document.getElementById('postCrop');
             postRequirementBtn = document.getElementById('postRequirement');

             if (postCropBtn) {
                 postCropBtn.textContent = 'Post Crop';
                 postCropBtn.onclick = null;
             }
             if (postRequirementBtn) {
                  postRequirementBtn.textContent = 'Post Requirement';
                  postRequirementBtn.onclick = null;
             }

             setupPostSubmitButtonListeners();
        }
    });
}

if (closePostModalBtn) {
    closePostModalBtn.addEventListener('click', () => {
        if (createPostModal) {
            createPostModal.style.display = 'none';
             postCropBtn = document.getElementById('postCrop');
             postRequirementBtn = document.getElementById('postRequirement');
             if (postCropBtn) postCropBtn.textContent = 'Post Crop';
             if (postRequirementBtn) postRequirementBtn.textContent = 'Post Requirement';
             setupPostSubmitButtonListeners();
        }
    });
}

window.addEventListener('click', (event) => {
    if (event.target === createPostModal) {
        if (createPostModal) {
            createPostModal.style.display = 'none';
             postCropBtn = document.getElementById('postCrop');
             postRequirementBtn = document.getElementById('postRequirement');
             if (postCropBtn) postCropBtn.textContent = 'Post Crop';
             if (postRequirementBtn) postRequirementBtn.textContent = 'Post Requirement';
             setupPostSubmitButtonListeners();
        }
    }
});

function openEditPostModal(post) {
     const modal = document.getElementById('createPostForm');
    if (!modal) {
        console.error('Post creation/edit modal not found.');
        return;
    }

    modal.querySelector('h2').textContent = 'Edit Post';

    const isFarmer = post.user_type === 'farmer';

    // Get buttons and strip existing listeners by cloning
    const rawCropBtn = document.getElementById('postCrop');
    const rawReqBtn = document.getElementById('postRequirement');
    if (rawCropBtn) {
        const newBtn = rawCropBtn.cloneNode(true);
        rawCropBtn.parentNode.replaceChild(newBtn, rawCropBtn);
        postCropBtn = newBtn;
    } else {
        postCropBtn = null;
    }
    if (rawReqBtn) {
        const newBtn = rawReqBtn.cloneNode(true);
        rawReqBtn.parentNode.replaceChild(newBtn, rawReqBtn);
        postRequirementBtn = newBtn;
    } else {
        postRequirementBtn = null;
    }


    if (postCropBtn) {
        postCropBtn.style.display = isFarmer ? 'block' : 'none';
         postCropBtn.onclick = () => savePostChanges(post.id, 'farmer');
         postCropBtn.textContent = 'Save Changes';
    }
    if (postRequirementBtn) {
        postRequirementBtn.style.display = !isFarmer ? 'block' : 'none';
         postRequirementBtn.onclick = () => savePostChanges(post.id, 'buyer');
         postRequirementBtn.textContent = 'Save Changes';
    }

    if (isFarmer) {
        document.getElementById('cropName').value = post.crop_name || '';
        document.getElementById('cropDetails').value = post.crop_details || '';
        document.getElementById('quantity').value = post.quantity || '';
        document.getElementById('location').value = post.location || '';

        const orgNameInput = document.getElementById('orgName');
        if (orgNameInput) {
             const container = orgNameInput.closest('div.create-post-form > *:has(#orgName)');
             if (container) container.style.display = 'none';
        }
         const orgTypeSelect = document.getElementById('orgType');
        if (orgTypeSelect) {
             const container = orgTypeSelect.closest('div.create-post-form > *:has(#orgType)');
             if (container) container.style.display = 'none';
        }
         const requirementsTextarea = document.getElementById('requirements');
        if (requirementsTextarea) {
             const container = requirementsTextarea.closest('div.create-post-form > *:has(#requirements)');
             if (container) container.style.display = 'none';
        }

    } else {
        document.getElementById('orgName').value = post.name || '';
        document.getElementById('orgType').value = post.organization || '';
        document.getElementById('requirements').value = post.requirements || '';
        document.getElementById('location').value = post.location || '';

         const cropNameInput = document.getElementById('cropName');
        if (cropNameInput) {
             const container = cropNameInput.closest('div.create-post-form > *:has(#cropName)');
             if (container) container.style.display = 'none';
        }
         const cropDetailsTextarea = document.getElementById('cropDetails');
        if (cropDetailsTextarea) {
             const container = cropDetailsTextarea.closest('div.create-post-form > *:has(#cropDetails)');
             if (container) container.style.display = 'none';
        }
         const quantityInput = document.getElementById('quantity');
        if (quantityInput) {
             const container = quantityInput.closest('div.create-post-form > *:has(#quantity)');
             if (container) container.style.display = 'none';
        }

    }
    const locationInput = document.getElementById('location');
     if (locationInput) {
         const container = locationInput.closest('div.create-post-form > *:has(#location)');
         if (container) container.style.display = 'block';
     }


    modal.style.display = 'block';
}

async function savePostChanges(postId, userType) {
    console.log("Attempting to save post changes for postId:", postId, "with userType:", userType);
    const postIndex = marketplacePosts.findIndex(post => post.id === postId);
    if (postIndex === -1) {
        alert('Error: Post not found.');
        console.error("Post not found for update, postId:", postId);
        return;
    }

    const post = marketplacePosts[postIndex];

    let updatedPostData = {};

    if (userType === 'farmer') {
        const cropName = document.getElementById('cropName').value.trim();
        const cropDetails = document.getElementById('cropDetails').value.trim();
        const quantity = document.getElementById('quantity').value.trim();
        const location = document.getElementById('location').value.trim();

         if (cropName && cropDetails && quantity && location) {
            updatedPostData = {
                crop_name: cropName,
                crop_details: cropDetails,
                quantity: quantity,
                location: location,
            };
         } else {
            alert('Please fill in all farmer post fields.');
            console.error("Missing farmer post fields for update.", { cropName, cropDetails, quantity, location });
            return;
         }

    } else {
        const orgName = document.getElementById('orgName').value.trim();
        const orgType = document.getElementById('orgType').value;
        const requirements = document.getElementById('requirements').value.trim();
        const location = document.getElementById('location').value.trim();

         if (orgName && orgType && requirements && location) {
            updatedPostData = {
                name: orgName,
                organization: orgType,
                requirements: requirements,
                location: location,
            };
        } else {
            alert('Please fill in all buyer requirement fields.');
            console.error("Missing buyer post fields for update.", { orgName, orgType, requirements, location });
            return;
        }
    }

    console.log("Sending updated post data to backend:", updatedPostData);

    try {
        const token = getAuthToken();
        if (!token) {
            alert('Authentication required to update a post.');
            console.error("No authentication token found for update post.");
            return;
        }

        const response = await fetch(`${API_BASE_URL}/api/posts/${postId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(updatedPostData)
        });

        const result = await response.json();

        if (response.ok) {
            console.log("Post updated successfully in backend:", result.post);
            alert('Post updated successfully!');
            if (createPostModal) createPostModal.style.display = 'none';
            await loadMarketplacePosts(); // Refresh all posts from the backend
            displayUserPosts(); // Also refresh user specific posts
         } else {
            console.error('Failed to update post. Status:', response.status, 'Error:', result.error);
            alert(`Failed to update post: ${result.error || 'Unknown error'}`);
         }
    } catch (error) {
        console.error('Error updating post:', error);
        alert('An error occurred while updating the post.');
    }

    // Do not re-bind create listeners here; the modal open handlers will set them as needed
}

function setupPostSubmitButtonListeners() {
     postCropBtn = document.getElementById('postCrop');
     postRequirementBtn = document.getElementById('postRequirement');

     const currentUserType = getCurrentUserType();

    if (postCropBtn) {
        const newPostCropBtn = postCropBtn.cloneNode(true);
        postCropBtn.parentNode.replaceChild(newPostCropBtn, postCropBtn);
        postCropBtn = newPostCropBtn;

        if (currentUserType === 'farmer' && postCropBtn.textContent === 'Post Crop') {
             postCropBtn.addEventListener('click', handlePostCreation);
        }
    }

     if (postRequirementBtn) {
        const newPostRequirementBtn = postRequirementBtn.cloneNode(true);
        postRequirementBtn.parentNode.replaceChild(newPostRequirementBtn, postRequirementBtn);
        postRequirementBtn = newPostRequirementBtn;
        if (currentUserType === 'buyer' && postRequirementBtn.textContent === 'Post Requirement') {
             postRequirementBtn.addEventListener('click', handlePostCreation);
        }
     }

      const farmerFields = ['cropName', 'cropDetails', 'quantity'];
      const buyerFields = ['orgName', 'orgType', 'requirements'];
      const commonFields = ['location'];

       farmerFields.forEach(id => {
           const input = document.getElementById(id);
           if (input) {
               const container = input.closest('div.create-post-form > *:has(#' + id + ')');
               if (container) container.style.display = (currentUserType === 'farmer') ? 'block' : 'none';
           }
       });

        buyerFields.forEach(id => {
           const input = document.getElementById(id);
           if (input) {
              const container = input.closest('div.create-post-form > *:has(#' + id + ')');
               if (container) container.style.display = (currentUserType === 'buyer') ? 'block' : 'none';
           }
       });

        commonFields.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                const container = input.closest('div.create-post-form > *:has(#' + id + ')');
                 if (container) container.style.display = 'block';
    }
  });
}


async function handlePostCreation() {
    console.log("handlePostCreation called");
    const currentUserType = getCurrentUserType();
    const authorId = getCurrentUserId();

    if (!authorId) {
        alert('User not logged in.');
        return;
    }

    let newPost = null;

    if (currentUserType === 'farmer') {
        const cropNameInput = document.getElementById('cropName');
        const cropDetailsTextarea = document.getElementById('cropDetails');
        const quantityInput = document.getElementById('quantity');
        const locationInput = document.getElementById('location');

         if (!cropNameInput || !cropDetailsTextarea || !quantityInput || !locationInput) {
             console.error("Farmer post input elements not found.");
             alert("An error occurred with the form.");
             return;
         }

        const cropName = cropNameInput.value.trim();
        const cropDetails = cropDetailsTextarea.value.trim();
        const quantity = quantityInput.value.trim();
        const location = locationInput.value.trim();

        console.log("Farmer Post Data:", { cropName, cropDetails, quantity, location });


        if (cropName && cropDetails && quantity && location) {
            newPost = {
                user_type: 'farmer',
                crop_name: cropName,
                crop_details: cropDetails,
                quantity: quantity,
                location: location,
                author_id: authorId,
            };
        } else {
            alert('Please fill in all farmer post fields.');
            return;
        }
      } else {
         const orgNameInput = document.getElementById('orgName');
         const orgTypeSelect = document.getElementById('orgType');
         const requirementsTextarea = document.getElementById('requirements');
         const locationInput = document.getElementById('location');

         if (!orgNameInput || !orgTypeSelect || !requirementsTextarea || !locationInput) {
             console.error("Buyer requirement input elements not found.");
              alert("An error occurred with the form.");
              return;
         }

        const orgName = orgNameInput.value.trim();
        const orgType = orgTypeSelect.value;
        const requirements = requirementsTextarea.value.trim();
        const location = locationInput.value.trim();

         console.log("Buyer Post Data:", { orgName, orgType, requirements, location });


         if (orgName && orgType && requirements && location) {
             newPost = {
                 user_type: 'buyer',
                 name: orgName,
                 organization: orgType,
                 requirements: requirements,
                 location: location,
                 author_id: authorId,
             };
        } else {
             alert('Please fill in all buyer requirement fields.');
             return;
         }
    }

    if (newPost) {
        // Send the new post to the backend API
        try {
            const token = getAuthToken();
            if (!token) {
                alert('Authentication required to create a post.');
                return;
            }

            const response = await fetch(`${API_BASE_URL}/api/posts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(newPost)
            });

            const result = await response.json();

            if (response.ok) {
                console.log("Post created successfully in backend:", result.post);
        if (createPostModal) createPostModal.style.display = 'none';
         alert('Post created successfully!');
                // Refresh all posts from the backend
                await loadMarketplacePosts();
                displayUserPosts(); // Also refresh user specific posts

            } else {
                console.error('Failed to create post:', result.error);
                alert(`Failed to create post: ${result.error}`);
            }
        } catch (error) {
            console.error('Error creating post:', error);
            alert('An error occurred while creating the post.');
        }
    }
}


async function deletePost(postId) {
    try {
        const token = getAuthToken();
        if (!token) {
            alert('Authentication required to delete a post.');
            return;
        }

        const response = await fetch(`${API_BASE_URL}/api/posts/${postId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const result = await response.json();

        if (response.ok) {
            console.log("Post deleted successfully in backend.");
     alert('Post deleted.');
            await loadMarketplacePosts(); // Refresh all posts from the backend
            displayUserPosts(); // Also refresh user specific posts
        } else {
            console.error('Failed to delete post:', result.error);
            alert(`Failed to delete post: ${result.error}`);
        }
    } catch (error) {
        console.error('Error deleting post:', error);
        alert('An error occurred while deleting the post.');
    }
}


// --- Chat Interface Functions ---

function displayConversationsList() {
    const currentUser = getCurrentUser();
    if (!currentUser || !conversationList) return;

    conversationList.innerHTML = '';

    const conversations = {};
     for (const chatId in userChats) {
         const participants = chatId.split('-');
         if (participants.includes(currentUser)) {
             const otherUser = participants.find(user => user !== currentUser);
             if (otherUser) {
                  const chat = userChats[chatId];
                  const messages = chat.messages;
                  const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null;
                  conversations[otherUser] = {
                      chatId: chatId,
                      lastMessage: lastMessage,
                  };
             }
         }
     }


    const contactIds = Object.keys(conversations);

    if (contactIds.length > 0) {
        contactIds.forEach(contactId => {
            const conversation = conversations[contactId];
            const contactProfile = userProfiles[contactId] || {};
            const contactDisplayName = contactProfile.name || contactId;
            const lastMessageText = conversation.lastMessage ?
                                    (conversation.lastMessage.sender === currentUser ? 'You: ' : '') + conversation.lastMessage.text :
                                    'No messages yet';
            const lastMessageTimestamp = conversation.lastMessage ? new Date(conversation.lastMessage.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';


            const listItem = document.createElement('li');
            listItem.classList.add('conversation-item');
            listItem.dataset.contactId = contactId;

             listItem.innerHTML = `
                 <div class="chat-avatar">
                     <img src="profile.png" alt="Avatar" class="avatar">
                 </div>
                 <div class="conversation-info">
                     <div class="contact-name">${contactDisplayName}</div>
                     <div class="last-message-preview">${lastMessageText}</div>
                 </div>
                 <div class="conversation-meta">
                     <div class="last-message-timestamp">${lastMessageTimestamp}</div>
                     <div class="unread-indicator" style="display: none;">0</div>
                 </div>
             `;

            listItem.addEventListener('click', () => {
                openChat(currentUser, contactId);
                 conversationList.querySelectorAll('.conversation-item').forEach(item => item.classList.remove('active'));
                listItem.classList.add('active');

                if (window.innerWidth <= 768 && chatListPanel && chatWindowPanel) {
                     chatListPanel.style.display = 'none';
                     chatWindowPanel.classList.add('active-chat');
                }
            });
            conversationList.appendChild(listItem);
        });
    } else {
        conversationList.innerHTML = '<p style="text-align: center; padding-top: 20px;">No active conversations.</p>';
    }

    if (window.innerWidth > 768 && chatWindowPanel) {
         chatWindowPanel.classList.remove('active-chat');
         chatWindowPanel.style.display = 'flex';
    } else if (window.innerWidth <= 768 && chatWindowPanel) {
         chatWindowPanel.classList.remove('active-chat');
         chatWindowPanel.style.display = 'none';
    }
}

function openChat(user1, user2) {
    // user2 is expected to be other user's ID
    const otherUserId = user2;

    // Update chat header with other user's display name
    const updateHeaderWithName = async () => {
        let displayName = (userProfiles[otherUserId] && userProfiles[otherUserId].name) || null;
        if (!displayName) {
            displayName = await fetchAndCacheUserPublicName(otherUserId) || otherUserId;
        }
        let headerEl = activeChatHeader;
        if (!headerEl && chatWindowPanel) {
            headerEl = document.createElement('div');
            headerEl.className = 'chat-header';
            chatWindowPanel.prepend(headerEl);
        }
        if (headerEl) {
            headerEl.innerHTML = '';
            const contactNameSpan = document.createElement('span');
            contactNameSpan.textContent = displayName;
            contactNameSpan.style.color = '#2d7a2d';
            contactNameSpan.style.fontWeight = '600';
            headerEl.appendChild(contactNameSpan);

            const closeBtn = document.createElement('button');
            closeBtn.classList.add('close-chat-panel');
            closeBtn.innerHTML = '&times;';
            closeBtn.addEventListener('click', () => {
                if (chatWindowPanel) chatWindowPanel.classList.remove('active-chat');
                if (chatListPanel) chatListPanel.style.display = 'flex';
            });
            headerEl.appendChild(closeBtn);
        }
    };

    // Create or get chat from backend, then load messages and wire send
    createOrGetChat(otherUserId).then(chat => {
        if (!chat) return;
        if (chatWindowPanel) chatWindowPanel.classList.add('active-chat');
        updateHeaderWithName();
        displayChatHistoryFromBackend(chat.id);
        wireSendMessage(chat.id);
    });

    const otherUserProfile = userProfiles[user2] || {};
    const otherUserDisplayName = otherUserProfile.name || user2;

    if (activeChatHeader) {
        activeChatHeader.innerHTML = '';
        const contactNameSpan = document.createElement('span');
        contactNameSpan.textContent = otherUserDisplayName;
        activeChatHeader.appendChild(contactNameSpan);

        const closeBtn = document.createElement('button');
        closeBtn.classList.add('close-chat-panel');
        closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', () => {
             if (chatWindowPanel) chatWindowPanel.classList.remove('active-chat');
             if (chatListPanel) chatListPanel.style.display = 'flex';
         });
        activeChatHeader.appendChild(closeBtn);

    }


    if (chatWindowPanel) chatWindowPanel.classList.add('active-chat');


    sendMessageBtn = document.getElementById('sendMessage');
    // send button wiring moved to wireSendMessage
}

function handleChatInputKeypress(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        const messageText = chatInput.value.trim();
        const chatId = chatInput.dataset.chatId;
        const currentUser = getCurrentUserId();

         if (messageText && chatId && currentUser) {
             sendChatMessageToBackend(chatId, messageText);
        chatInput.value = '';
      }
    }
}

async function displayChatHistoryFromBackend(chatId) {
    if (!chatMessagesContainer) return;
    chatMessagesContainer.innerHTML = '';

    const currentUser = getCurrentUserId();
    try {
        const token = getAuthToken();
        const res = await fetch(`${API_BASE_URL}/api/chats/${chatId}/messages`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) return;
        const data = await res.json();
        const messages = data.messages || [];

        messages.forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message');
        messageElement.classList.add(message.sender === currentUser ? 'sent' : 'received');

         if (message.sender !== currentUser) {
            const senderSpan = document.createElement('span');
            senderSpan.className = 'sender';
            const senderProfile = userProfiles[message.sender] || {};
            senderSpan.textContent = senderProfile.name || message.sender;
            messageElement.appendChild(senderSpan);
         }


        const textNode = document.createTextNode(message.message || message.text);
        messageElement.appendChild(textNode);

        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'timestamp';
        const messageDate = new Date(message.created_at || message.timestamp);
        const options = { hour: '2-digit', minute: '2-digit', hour12: true };
        timestampSpan.textContent = messageDate.toLocaleTimeString('en-US', options);
        messageElement.appendChild(timestampSpan);


        chatMessagesContainer.appendChild(messageElement);
    });

    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    } catch {}
}

async function sendChatMessageToBackend(chatId, messageText) {
    try {
        if (!chatId) {
            console.error('sendChatMessageToBackend: Missing chatId');
            return;
        }
        console.log('Sending message to chat', chatId, 'text:', messageText);
        const token = getAuthToken();
        const res = await fetch(`${API_BASE_URL}/api/chats/${chatId}/messages`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText })
        });
        if (!res.ok) {
            const err = await res.text();
            console.error('Message send failed', res.status, err);
            return;
        }
        await displayChatHistoryFromBackend(chatId);
        await displayConversationsList();
    } catch {}
}

async function createOrGetChat(otherUserId) {
    try {
        const token = getAuthToken();
        if (!token) {
            console.error('createOrGetChat: No auth token found');
            alert('Please login to start a chat');
            return null;
        }
        
        if (!otherUserId) {
            console.error('createOrGetChat: missing otherUserId');
            return null;
        }

        console.log('Creating/Getting chat with', otherUserId);
        const res = await fetch(`${API_BASE_URL}/api/chats`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`, 
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ other_user_id: otherUserId })
        });

        // Add detailed error logging
        if (!res.ok) {
            let errorData;
            try {
                errorData = await res.json();
                console.error('createOrGetChat failed', {
                    status: res.status,
                    statusText: res.statusText,
                    error: errorData.error || 'Unknown error',
                    url: res.url,
                    headers: Object.fromEntries(res.headers.entries())
                });
            } catch (e) {
                console.error('Failed to parse error response:', e);
                errorData = {};
            }
            
            let errorMessage = 'Failed to open chat. ';
            if (res.status === 401) {
                errorMessage += 'Session expired, please login again.';
            } else if (res.status === 404) {
                errorMessage += 'User not found.';
            } else if (res.status === 500) {
                errorMessage += 'Server error occurred.';
            } else {
                errorMessage += 'Please try again.';
            }
            
            alert(errorMessage);
            return null;
        }

        const data = await res.json();
        if (!data.chat) {
            console.error('createOrGetChat: No chat data in response', data);
            alert('Chat creation failed. Please try again.');
            return null;
        }

        console.log('Chat created/retrieved successfully:', data.chat);
        return data.chat;
    } catch (error) {
        console.error('createOrGetChat network error:', error);
        alert('Network error occurred. Please check your connection and try again.');
        return null;
    }
}

function wireSendMessage(chatId) {
    sendMessageBtn = document.getElementById('sendMessage');
    chatInput = document.getElementById('chatInput');
    if (sendMessageBtn && chatInput) {
        const newSendMessageBtn = sendMessageBtn.cloneNode(true);
        sendMessageBtn.parentNode.replaceChild(newSendMessageBtn, sendMessageBtn);
        sendMessageBtn = newSendMessageBtn;
        sendMessageBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const messageText = chatInput.value.trim();
            if (messageText) {
                sendChatMessageToBackend(chatId, messageText);
                chatInput.value = '';
            }
        });
        if (chatInput) {
            chatInput.removeEventListener('keypress', handleChatInputKeypress);
            chatInput.addEventListener('keypress', handleChatInputKeypress);
        }
        sendMessageBtn.dataset.chatId = chatId;
        if (chatInput) chatInput.dataset.chatId = chatId;
    } else {
        // Fallback: if button not in DOM yet, retry shortly
        setTimeout(() => wireSendMessage(chatId), 100);
    }
}

if (chatSearchInput && conversationList) {
    chatSearchInput.addEventListener('input', () => {
        const searchTerm = chatSearchInput.value.toLowerCase();
        const conversationItems = conversationList.querySelectorAll('.conversation-item');

        conversationItems.forEach(item => {
            const contactName = item.querySelector('.contact-name')?.textContent.toLowerCase() || '';
            const lastMessagePreview = item.querySelector('.last-message-preview')?.textContent.toLowerCase() || '';

            if (contactName.includes(searchTerm) || lastMessagePreview.includes(searchTerm)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
}


// --- Edit Profile Functions ---

function populateEditProfileForm() {
    const currentUser = getCurrentUser();
    if (!currentUser || !profileEditForm) return;

    const userProfile = userProfiles[currentUser] || {};

    if (editUserNameInput) editUserNameInput.value = userProfile.name || '';
    if (editUserContactInput) editUserContactInput.value = userProfile.contact || '';
}

if (saveProfileBtn) {
    saveProfileBtn.addEventListener('click', () => {
        const currentUser = getCurrentUser();
        if (!currentUser || !profileEditForm) return;

        const userName = editUserNameInput ? editUserNameInput.value.trim() : '';
        const userContact = editUserContactInput ? editUserContactInput.value.trim() : '';

        if (userName) {
             userProfiles[currentUser] = {
                 ...userProfiles[currentUser],
                 name: userName,
                 contact: userContact,
                 userType: getCurrentUserType()
             };
             localStorage.setItem('userProfiles', JSON.stringify(userProfiles));
             alert('Profile saved successfully!');
             populateProfileDropdown();
             if (chatsSection && chatsSection.style.display !== 'none') {
                  displayConversationsList();
             }
        } else {
            alert('Name is required to save profile.');
        }
    });
}


// --- Initial Load ---
document.addEventListener('DOMContentLoaded', () => {
    const currentUser = getCurrentUser();
    if (currentUser) {
        showSection(marketplaceSection, 'navMarketplace');
        displayPosts();
        populateProfileDropdown();
    } else {
        window.location.href = 'index.htm';
    }

    setupCreatePostButtonListener();
    setupPostSubmitButtonListeners();
});

const locationSearchInput = document.getElementById('locationSearch');
if (locationSearchInput) {
    locationSearchInput.addEventListener('input', () => {
        const searchTerm = locationSearchInput.value.toLowerCase();
        const isFarmerPage = getCurrentUserType() === 'farmer';
        const postTypeToDisplay = isFarmerPage ? 'buyer' : 'farmer';

        // Filter client-side on the posts already loaded into marketplacePosts
        const filtered = (marketplacePosts || []).filter(post => {
            const postLocation = post.location ? post.location.toLowerCase() : '';
            const postCropName = post.crop_name ? post.crop_name.toLowerCase() : '';
            const postBuyerName = post.name ? post.name.toLowerCase() : '';
            const postRequirements = post.requirements ? post.requirements.toLowerCase() : '';

            return post && post.user_type === postTypeToDisplay &&
                   (postLocation.includes(searchTerm) ||
                    (post.user_type === 'farmer' && postCropName.includes(searchTerm)) ||
                    (post.user_type === 'buyer' && (postBuyerName.includes(searchTerm) || postRequirements.includes(searchTerm)))
                   );
        });
        displayPosts(filtered);
    });
}

// Mobile Menu Toggle
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navbarRight = document.querySelector('.navbar-right');
    
    if (hamburger && navbarRight) {
      hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navbarRight.classList.toggle('active');
      });
      
      // Close menu when clicking outside
      document.addEventListener('click', (e) => {
        if (!navbarRight.contains(e.target) && !hamburger.contains(e.target)) {
          hamburger.classList.remove('active');
          navbarRight.classList.remove('active');
        }
      });
      
      // Close menu when clicking nav links
      document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
          hamburger.classList.remove('active');
          navbarRight.classList.remove('active');
        });
      });
    }
  }
  
  // Initialize when DOM loads
  document.addEventListener('DOMContentLoaded', initMobileMenu);