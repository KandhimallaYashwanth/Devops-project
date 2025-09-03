// Store data in localStorage
let marketplacePosts = JSON.parse(localStorage.getItem('marketplacePosts')) || [];
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
const activeChatHeader = chatWindowPanel ? chatWindowPanel.querySelector('.chat-header') : null;
const chatMessagesContainer = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
let sendMessageBtn = document.getElementById('sendMessage');
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
        localStorage.removeItem('userContact');
        localStorage.removeItem('currentUserType');
        window.location.href = 'index.htm';
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
  if (post.userType === 'farmer') {
    postContent = `
      <h3>${post.cropName}</h3>
      <p><strong>Details:</strong> ${post.cropDetails}</p>
      <p><strong>Quantity:</strong> ${post.quantity}</p>
      <p><strong>Location:</strong> ${post.location}</p>
       <p><strong>Posted:</strong> ${new Date(post.timestamp).toLocaleString()}</p>
    `;
  } else { // buyer post
    postContent = `
      <h3>${post.name}</h3>
      <p><strong>Organization:</strong> ${post.organization}</p>
      <p><strong>Location:</strong> ${post.location}</p>
      <p><strong>Requirements:</strong> ${post.requirements}</p>
       <p><strong>Posted:</strong> ${new Date(post.timestamp).toLocaleString()}</p>
    `;
  }

  const postActions = document.createElement('div');
  postActions.className = 'post-actions';

  if (!isUserPost) {
      const chatBtn = document.createElement('button');
      chatBtn.className = 'chat-btn';
      const authorProfile = userProfiles[post.authorId] || {};
      const authorDisplayName = authorProfile.name || post.authorId;

      chatBtn.textContent = `Chat with ${authorDisplayName}`;
      chatBtn.dataset.authorId = post.authorId;
       chatBtn.addEventListener('click', () => {
          const authorId = chatBtn.dataset.authorId;
          if (authorId) {
              openChat(getCurrentUser(), authorId);
              showSection(chatsSection, 'navChats');
               if (profileDropdownContent) profileDropdownContent.classList.remove('show');
          }
      });
      postActions.appendChild(chatBtn);
  }

   if (isUserPost) {
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

function displayPosts(filteredPosts = null) {
  const isFarmerPage = getCurrentUserType() === 'farmer';
  const postsContainer = isFarmerPage ? buyerPostsContainer : farmerPostsContainer;
  const postTypeToDisplay = isFarmerPage ? 'buyer' : 'farmer';

  const postsToDisplay = filteredPosts || marketplacePosts;

  
  if (postsContainer) {
    postsContainer.innerHTML = '';
    const relevantPosts = postsToDisplay.filter(post => {
        return post && post.userType && post.userType === postTypeToDisplay;
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

function displayUserPosts() {
    const currentUser = getCurrentUser();
    // The filter below already ensures only the current user's posts are displayed
    const userPosts = marketplacePosts.filter(post => post.authorId === currentUser);

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

    const isFarmer = post.userType === 'farmer';

    postCropBtn = document.getElementById('postCrop');
    postRequirementBtn = document.getElementById('postRequirement');


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
        document.getElementById('cropName').value = post.cropName || '';
        document.getElementById('cropDetails').value = post.cropDetails || '';
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

function savePostChanges(postId, userType) {
    const postIndex = marketplacePosts.findIndex(post => post.id === postId);
    if (postIndex === -1) {
        alert('Error: Post not found.');
        return;
    }

    const post = marketplacePosts[postIndex];

    if (userType === 'farmer') {
        const cropName = document.getElementById('cropName').value.trim();
        const cropDetails = document.getElementById('cropDetails').value.trim();
        const quantity = document.getElementById('quantity').value.trim();
        const location = document.getElementById('location').value.trim();

         if (cropName && cropDetails && quantity && location) {
             post.cropName = cropName;
             post.cropDetails = cropDetails;
             post.quantity = quantity;
             post.location = location;
              post.timestamp = new Date().toISOString();


             localStorage.setItem('marketplacePosts', JSON.stringify(marketplacePosts));
             alert('Post updated successfully!');
             if (createPostModal) createPostModal.style.display = 'none';
             displayUserPosts();
              if (marketplaceSection && marketplaceSection.style.display !== 'none' && getCurrentUserType() === 'buyer') {
                 displayPosts();
              }
         } else {
             alert('Please fill in all fields.');
         }

    } else {
        const orgName = document.getElementById('orgName').value.trim();
        const orgType = document.getElementById('orgType').value;
        const requirements = document.getElementById('requirements').value.trim();
        const location = document.getElementById('location').value.trim();

         if (orgName && orgType && requirements && location) {
             post.name = orgName;
             post.organization = orgType;
             post.requirements = requirements;
             post.location = location;
             post.timestamp = new Date().toISOString();


             localStorage.setItem('marketplacePosts', JSON.stringify(marketplacePosts));
             alert('Requirement updated successfully!');
             if (createPostModal) createPostModal.style.display = 'none';
             displayUserPosts();
              if (marketplaceSection && marketplaceSection.style.display !== 'none' && getCurrentUserType() === 'farmer') {
                 displayPosts();
              }
         } else {
             alert('Please fill in all fields.');
         }
    }
     setupCreatePostButtonListener();
     setupPostSubmitButtonListeners();
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


function handlePostCreation() {
    console.log("handlePostCreation called");
    const currentUserType = getCurrentUserType();
    const authorId = getCurrentUser();

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
                id: Date.now(),
                userType: 'farmer',
                cropName,
                cropDetails,
                quantity,
                location,
                authorId,
                timestamp: new Date().toISOString()
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
                 id: Date.now(),
                 userType: 'buyer',
                 name: orgName,
                 organization: orgType,
                 requirements,
                 location,
                 authorId,
                 timestamp: new Date().toISOString()
             };
        } else {
             alert('Please fill in all buyer requirement fields.');
             return;
         }
    }

    if (newPost) {
        console.log("New Post created:", newPost);
        marketplacePosts.push(newPost);
        localStorage.setItem('marketplacePosts', JSON.stringify(marketplacePosts));
        console.log("marketplacePosts after pushing:", marketplacePosts);

        const isFarmerPage = window.location.pathname.includes('farmer.html');
         const isBuyerPage = window.location.pathname.includes('buyer.html');

        if (marketplaceSection && marketplaceSection.style.display !== 'none') {
             if ((currentUserType === 'farmer' && isBuyerPage) || (currentUserType === 'buyer' && isFarmerPage)) {
                 console.log("Updating marketplace display");
                 displayPosts();
             }
        }

        if (myPostsSection && myPostsSection.style.display !== 'none') {
             if ((currentUserType === 'farmer' && isFarmerPage) || (currentUserType === 'buyer' && isBuyerPage)) {
                 console.log("Updating user posts display");
                 displayUserPosts();
             }
        }


        if (createPostModal) createPostModal.style.display = 'none';
         alert('Post created successfully!');
    }
}


function deletePost(postId) {
    const initialLength = marketplacePosts.length;
    marketplacePosts = marketplacePosts.filter(post => post.id !== postId);

    localStorage.setItem('marketplacePosts', JSON.stringify(marketplacePosts));

    displayUserPosts();

    const deletedPostWasVisibleInMarketplace = initialLength > marketplacePosts.length;
     if (deletedPostWasVisibleInMarketplace && marketplaceSection && marketplaceSection.style.display !== 'none') {
         displayPosts();
     }

     alert('Post deleted.');
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
    const chatId = [user1, user2].sort().join('-');

    if (!userChats[chatId]) {
        userChats[chatId] = { messages: [] };
        localStorage.setItem('userChats', JSON.stringify(userChats));
    }

    displayChatHistory(chatId);

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
    if (sendMessageBtn) {
         const newSendMessageBtn = sendMessageBtn.cloneNode(true);
         sendMessageBtn.parentNode.replaceChild(newSendMessageBtn, sendMessageBtn);
         sendMessageBtn = newSendMessageBtn;
         sendMessageBtn.addEventListener('click', () => {
             const messageText = chatInput.value.trim();
             if (messageText) {
                 sendChatMessage(chatId, messageText, user1);
                 chatInput.value = '';
             }
         });
         if (chatInput) {
             chatInput.removeEventListener('keypress', handleChatInputKeypress);
             chatInput.addEventListener('keypress', handleChatInputKeypress);
         }
         sendMessageBtn.dataset.chatId = chatId;
         if (chatInput) chatInput.dataset.chatId = chatId;
    }
}

function handleChatInputKeypress(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        const messageText = chatInput.value.trim();
        const chatId = chatInput.dataset.chatId;
        const currentUser = getCurrentUser();

         if (messageText && chatId && currentUser) {
             sendChatMessage(chatId, messageText, currentUser);
        chatInput.value = '';
      }
    }
}

function displayChatHistory(chatId) {
    const chat = userChats[chatId];
    if (!chat || !chatMessagesContainer) return;

    chatMessagesContainer.innerHTML = '';

    const currentUser = getCurrentUser();

    chat.messages.forEach(message => {
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


        const textNode = document.createTextNode(message.text);
        messageElement.appendChild(textNode);

        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'timestamp';
        const messageDate = new Date(message.timestamp);
        const options = { hour: '2-digit', minute: '2-digit', hour12: true };
        timestampSpan.textContent = messageDate.toLocaleTimeString('en-US', options);
        messageElement.appendChild(timestampSpan);


        chatMessagesContainer.appendChild(messageElement);
    });

    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

function sendChatMessage(chatId, messageText, sender) {
    const chat = userChats[chatId];
    if (!chat) return;

    const newMessage = {
        sender: sender,
        text: messageText,
        timestamp: new Date().toISOString()
    };

    chat.messages.push(newMessage);
    localStorage.setItem('userChats', JSON.stringify(userChats));

    displayChatHistory(chatId);
    displayConversationsList();
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

        const filtered = marketplacePosts.filter(post => {
            const postLocation = post.location ? post.location.toLowerCase() : '';
            const postCropName = post.cropName ? post.cropName.toLowerCase() : '';
            const postBuyerName = post.name ? post.name.toLowerCase() : '';
            const postRequirements = post.requirements ? post.requirements.toLowerCase() : '';

            return post && post.userType === postTypeToDisplay &&
                   (postLocation.includes(searchTerm) ||
                    (post.userType === 'farmer' && postCropName.includes(searchTerm)) ||
                    (post.userType === 'buyer' && (postBuyerName.includes(searchTerm) || postRequirements.includes(searchTerm)))
                   );
        });
        displayPosts(filtered);
    });
}
