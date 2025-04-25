// Add custom class to sections for styling
document.addEventListener('DOMContentLoaded', (event) => {
    setTimeout(() => {
        const headers = document.querySelectorAll('.stMarkdown h1, .stMarkdown h2, .stMarkdown h3');
        headers.forEach(header => {
            const section = header.closest('.element-container').parentElement;
            section.classList.add('section-card');
        });
    }, 1000);
});

// This function handles navbar styling
function styleNavbar() {
    const header = document.querySelector('header[data-testid="stHeader"]');
    if (header) {
        header.style.background = 'linear-gradient(90deg, #1e3c72 0%, #2a5298 100%)';
        header.style.backgroundImage = 'linear-gradient(90deg, #1e3c72 0%, #2a5298 100%)';
        
        // Force all child elements to be transparent
        const headerDivs = header.querySelectorAll('div');
        headerDivs.forEach(div => {
            div.style.backgroundColor = 'transparent';
            div.style.background = 'transparent';
        });
    }
}

// Function to apply gradient styling to elements
function applyGradients() {
    // Apply to file uploaders and ensure text is visible
    document.querySelectorAll('[data-testid="stFileUploader"]').forEach(el => {
        el.style.background = 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(44, 82, 130, 0.8) 100%)';
        el.style.borderRadius = '8px';
        el.style.padding = '12px';
        el.style.border = '1px solid rgba(255, 255, 255, 0.2)';
        
        // Target all text elements inside the uploader
        const textElements = el.querySelectorAll('p, span, div, small, label');
        textElements.forEach(text => {
            text.style.color = 'black';
            text.style.textShadow = 'none';
            text.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
            text.style.padding = '2px 5px';
            text.style.borderRadius = '4px';
        });
        
        // Specifically look for the drag and drop message
        const dragDropText = el.querySelector('.uploadMessage') || 
                              el.querySelector('[data-testid="stMarkdownContainer"]');
        if (dragDropText) {
            dragDropText.style.color = 'black';
            dragDropText.style.textShadow = 'none';
            dragDropText.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
            dragDropText.style.padding = '4px 8px';
            dragDropText.style.borderRadius = '4px';
            dragDropText.style.fontWeight = '500';
        }
    });
    
    // Apply to all form controls
    document.querySelectorAll('input, select, textarea').forEach(el => {
        const parent = el.closest('div');
        if (parent && !parent.classList.contains('gradient-applied')) {
            parent.style.background = 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(44, 82, 130, 0.8) 100%)';
            parent.style.borderRadius = '6px';
            parent.classList.add('gradient-applied');
        }
    });
    
    // Apply to segment order areas and sortable lists
    document.querySelectorAll('[data-testid="stVerticalBlock"] > div').forEach(el => {
        if (el.style.overflow === 'auto' || el.style.overflowY === 'auto') {
            el.style.background = 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(44, 82, 130, 0.8) 100%)';
            el.style.borderRadius = '8px';
            el.style.padding = '8px';
            el.style.border = '1px solid rgba(255, 255, 255, 0.2)';
        }
    });
    
    // Apply to widget containers
    document.querySelectorAll('.row-widget').forEach(el => {
        el.style.background = 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(44, 82, 130, 0.8) 100%)';
        el.style.borderRadius = '8px';
        el.style.padding = '8px';
        el.style.marginBottom = '8px';
    });
    
    // Apply to upload buttons specifically
    document.querySelectorAll('.uploadButton, [data-testid="stFileUploadDropzone"]').forEach(el => {
        el.style.background = 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(44, 82, 130, 0.8) 100%)';
        el.style.borderRadius = '8px';
        el.style.padding = '8px';
        el.style.border = '1px solid rgba(255, 255, 255, 0.2)';
        el.style.color = 'white';
    });
    
    // Enhance number inputs - make text black on white background
    document.querySelectorAll('[data-testid="stNumberInput"] input, .stNumberInput input').forEach(el => {
        el.style.background = 'white';
        el.style.borderRadius = '6px';
        el.style.color = 'black';
        el.style.border = '1px solid rgba(30, 41, 59, 0.4)';
        el.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
        el.style.padding = '6px 12px';
        el.style.fontWeight = '500';
        el.style.textShadow = 'none';
    });
}

// Function to style text inputs, popups and modals with black text
function styleInputsAndPopups() {
    // Style text inputs
    document.querySelectorAll('.stTextInput input, textarea').forEach(el => {
        el.style.color = 'black';
        el.style.background = 'white';
        el.style.fontWeight = '500';
        el.style.textShadow = 'none';
        // Style the parent container
        const container = el.closest('[data-baseweb="input"], [data-baseweb="textarea"]');
        if (container) {
            container.style.background = 'white';
            container.style.border = '1px solid rgba(30, 41, 59, 0.4)';
            container.style.borderRadius = '6px';
        }
    });
    
    // Style select boxes
    document.querySelectorAll('.stSelectbox [data-baseweb="select"], .stMultiSelect [data-baseweb="select"]').forEach(el => {
        el.querySelectorAll('div').forEach(div => {
            div.style.background = 'white';
            div.style.backgroundColor = 'white';
        });
        el.querySelectorAll('span').forEach(span => {
            span.style.color = 'black';
            span.style.fontWeight = '500';
        });
    });
    
    // Style dropdown menus and their items
    document.querySelectorAll('[data-baseweb="popover"], [data-baseweb="menu"], [data-baseweb="select"] ul').forEach(el => {
        el.style.backgroundColor = 'white';
        
        el.querySelectorAll('li').forEach(li => {
            li.style.backgroundColor = 'white';
            li.style.color = 'black';
            
            // Selected item
            if (li.getAttribute('aria-selected') === 'true') {
                li.style.backgroundColor = '#4CAF50';
                li.style.color = 'white';
            }
        });
    });
    
    // Style popups, tooltips and modals
    document.querySelectorAll('div[data-baseweb="popover"], div[role="tooltip"], div[data-modal="true"], div[role="dialog"]').forEach(el => {
        el.querySelectorAll('div, span, p, a, label').forEach(textEl => {
            textEl.style.color = 'black';
        });
    });
    
    // Look for specific segment order inputs
    document.querySelectorAll('div[data-testid="stVerticalBlock"] input').forEach(el => {
        el.style.color = 'black';
        el.style.background = 'white';
    });
}

// Update the forceSelectBoxTextColor function to handle labels
function forceSelectBoxTextColor() {
    // Target all select boxes
    document.querySelectorAll('.stSelectbox, [data-testid="stSelectbox"], .stMultiSelect').forEach(selectBox => {
        // Style the labels/headings
        selectBox.querySelectorAll('label').forEach(label => {
            label.style.color = 'black';
            label.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
            label.style.padding = '2px 6px';
            label.style.borderRadius = '4px';
            label.style.fontWeight = '500';
            label.style.marginBottom = '5px';
            label.style.display = 'inline-block';
        });
        
        // Style all possible text elements inside
        selectBox.querySelectorAll('div, span, input, p').forEach(el => {
            el.style.color = 'black';
            el.style.backgroundColor = 'white';
            // Only for text elements
            if (el.tagName === 'SPAN' || el.tagName === 'P' || el.tagName === 'INPUT') {
                el.style.color = 'black';
                el.style.textShadow = 'none';
                el.style.fontWeight = '500';
            }
        });
        
        // Explicitly target the value container
        const valueContainer = selectBox.querySelector('[data-baseweb="value"], [data-baseweb="select"]');
        if (valueContainer) {
            valueContainer.style.backgroundColor = 'white';
            valueContainer.querySelectorAll('span, div').forEach(el => {
                el.style.color = 'black';
                el.style.backgroundColor = 'white';
            });
        }
    });
    
    // Also target all form labels for inputs, checkboxes, radio buttons, etc.
    document.querySelectorAll('label').forEach(label => {
        // Check if this label is for a form element (not a header/title)
        const isFormLabel = label.htmlFor || 
                           label.closest('.stSelectbox, .stNumberInput, .stTextInput, .stMultiSelect, .stCheckbox, .stRadio');
        
        if (isFormLabel) {
            label.style.color = 'black';
            label.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
            label.style.padding = '2px 6px';
            label.style.borderRadius = '4px';
            label.style.fontWeight = '500';
        }
    });
    
    // Target dropdown menus when they're open
    document.querySelectorAll('[data-baseweb="menu"], [data-baseweb="popover"]').forEach(menu => {
        menu.style.backgroundColor = 'white';
        menu.style.color = 'black';
        
        menu.querySelectorAll('ul, li').forEach(el => {
            el.style.backgroundColor = 'white';
            el.style.color = 'black';
        });
        
        // Special case for selected items
        menu.querySelectorAll('li[aria-selected="true"]').forEach(el => {
            el.style.backgroundColor = '#4CAF50';
            el.style.color = 'white';
        });
    });
}

// Function to style all form labels and headers
function styleFormLabels() {
    // Target all types of labels
    document.querySelectorAll('label, [data-testid="stWidgetLabel"]').forEach(label => {
        // Apply standard styling to ALL labels for consistency
        label.style.color = 'black';
        label.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        label.style.padding = '2px 8px';
        label.style.borderRadius = '4px';
        label.style.fontWeight = '500';
        label.style.marginBottom = '5px';
        label.style.display = 'inline-block';
        label.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
        label.style.fontSize = '14px';
        label.style.maxWidth = '95%';
        label.style.zIndex = '100';
        label.style.position = 'relative';
    });
    
    // Look for specific time-related widget labels (common for time selectors)
    document.querySelectorAll('[data-testid="stWidgetLabel"]').forEach(label => {
        const text = label.textContent.toLowerCase();
        if (text.includes('time') || text.includes('start') || 
            text.includes('end') || text.includes('select')) {
            label.style.color = 'black';
            label.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            label.style.padding = '3px 8px';
            label.style.fontWeight = '600';
        }
    });
    
    // Target all text inside form widgets to ensure black text
    document.querySelectorAll('.stSelectbox, .stTextInput, .stNumberInput, .stTextArea, .stDateInput, .stTimeInput, .stMultiSelect').forEach(widget => {
        widget.querySelectorAll('*:not(label)').forEach(el => {
            el.style.color = 'black';
        });
    });
    
    // Special handling for sliders
    document.querySelectorAll('.stSlider').forEach(slider => {
        // Style the label
        const sliderLabel = slider.querySelector('[data-testid="stWidgetLabel"]');
        if (sliderLabel) {
            sliderLabel.style.marginBottom = '10px';
            sliderLabel.style.fontWeight = '600';
            sliderLabel.style.padding = '3px 10px';
        }
        
        // Style the slider thumb and track
        slider.querySelectorAll('div[role="slider"]').forEach(thumb => {
            thumb.style.color = 'black';
            thumb.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
            thumb.style.borderRadius = '50%';
        });
        
        // Style all text elements in the slider
        slider.querySelectorAll('span, div[data-baseweb="thumb-value"]').forEach(text => {
            text.style.color = 'black';
            text.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
            text.style.padding = '1px 4px';
            text.style.borderRadius = '3px';
        });
    });
}

// Function to specifically style slider headers like Bass, EQ, Volume
function styleSliderHeaders() {
    // Look for specific text content in labels and widget labels
    const targetTexts = ['bass', 'eq', 'volume', 'pitch', 'treble', 'mid', 'crossfade'];
    
    // Find all labels and check if they match our target texts
    document.querySelectorAll('label, [data-testid="stWidgetLabel"]').forEach(label => {
        const text = label.textContent.toLowerCase();
        
        // Check if the label contains any of our target texts
        if (targetTexts.some(target => text.includes(target))) {
            // Force styling using inline style with !important-like priority
            label.style.setProperty('color', 'black', 'important');
            label.style.setProperty('background-color', 'rgba(255, 255, 255, 0.95)', 'important');
            label.style.setProperty('font-weight', '600', 'important');
            label.style.setProperty('padding', '3px 10px', 'important');
            label.style.setProperty('border-radius', '4px', 'important');
            label.style.setProperty('display', 'inline-block', 'important');
            label.style.setProperty('margin-bottom', '5px', 'important');
            
            // Ensure text nodes directly inside the label are black
            for (let node of label.childNodes) {
                if (node.nodeType === Node.TEXT_NODE) {
                    // Wrap text node in a span to apply styling
                    const span = document.createElement('span');
                    span.textContent = node.textContent;
                    span.style.color = 'black';
                    span.style.fontWeight = '600';
                    node.parentNode.replaceChild(span, node);
                }
            }
            
            // Make sure all child elements also have black text
            label.querySelectorAll('*').forEach(child => {
                child.style.setProperty('color', 'black', 'important');
                child.style.setProperty('text-shadow', 'none', 'important');
                
                // Ensure any text nodes inside this element are also wrapped
                for (let node of child.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                        const span = document.createElement('span');
                        span.textContent = node.textContent;
                        span.style.color = 'black';
                        node.parentNode.replaceChild(span, node);
                    }
                }
            });
        }
    });
    
    // Also target all slider labels directly
    document.querySelectorAll('.stSlider [data-testid="stWidgetLabel"], .stSlider label').forEach(label => {
        label.style.setProperty('color', 'black', 'important');
        label.style.setProperty('background-color', 'rgba(255, 255, 255, 0.95)', 'important');
        label.style.setProperty('font-weight', '600', 'important');
        label.style.setProperty('padding', '3px 10px', 'important');
        label.style.setProperty('border-radius', '4px', 'important');
        label.style.setProperty('display', 'inline-block', 'important');
        label.style.setProperty('margin-bottom', '5px', 'important');
        
        // Ensure all child elements inherit black text color
        label.querySelectorAll('*').forEach(child => {
            child.style.setProperty('color', 'black', 'important');
            child.style.setProperty('text-shadow', 'none', 'important');
        });
    });
}

// Add a special fix for Streamlit's widget structure where text might be in nested divs
function fixStreamlitWidgetText() {
    // Find all possible slider elements
    document.querySelectorAll('.stSlider').forEach(slider => {
        // Target all text-containing elements
        slider.querySelectorAll('div, span, p').forEach(el => {
            // Check if this element has text directly inside it
            if (el.childNodes.length > 0) {
                let hasTextNode = false;
                
                // Check each child node
                for (let node of el.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                        hasTextNode = true;
                        break;
                    }
                }
                
                // If it has text, ensure it's styled properly
                if (hasTextNode || el.innerText.trim()) {
                    el.style.color = 'black';
                    
                    // If it's likely a header or label
                    if (el.parentElement && 
                        (el.parentElement.classList.contains('stSlider') || 
                        el.parentElement.querySelector('input[type="range"]'))) {
                        el.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
                        el.style.padding = '3px 10px';
                        el.style.borderRadius = '4px';
                        el.style.display = 'inline-block';
                    }
                }
            }
        });
        
        // Special case for the top div that often contains the label text
        const firstDiv = slider.firstElementChild;
        if (firstDiv && firstDiv.firstElementChild) {
            const labelDiv = firstDiv.firstElementChild;
            labelDiv.style.color = 'black';
            labelDiv.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            labelDiv.style.padding = '3px 10px';
            labelDiv.style.borderRadius = '4px';
            labelDiv.style.display = 'inline-block';
            
            // Force all text inside to be black
            labelDiv.querySelectorAll('*').forEach(child => {
                child.style.color = 'black';
            });
        }
    });
}

// Extreme approach to force slider labels to black text
function extremeForceSliderLabels() {
    try {
        // Target all sliders
        document.querySelectorAll('.stSlider').forEach(slider => {
            // Get the first few divs where the label usually is
            const possibleLabelContainers = [
                slider.querySelector('div:first-child'),
                slider.querySelector('div:first-child > div:first-child'),
                slider.querySelector('[data-testid="stWidgetLabel"]'),
                slider.querySelector('label')
            ];
            
            possibleLabelContainers.forEach(container => {
                if (container) {
                    // Create a completely new div with our styling
                    const newDiv = document.createElement('div');
                    newDiv.textContent = container.textContent;
                    newDiv.style.cssText = `
                        color: black !important;
                        background-color: rgba(255, 255, 255, 0.95) !important;
                        border-radius: 4px !important;
                        padding: 3px 10px !important;
                        margin-bottom: 8px !important;
                        display: inline-block !important;
                        font-weight: 600 !important;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
                        position: relative;
                        z-index: 1000;
                    `;
                    
                    // Insert our new div before the container
                    if (container.parentNode) {
                        container.parentNode.insertBefore(newDiv, container);
                        
                        // And hide the original container if it's not essential
                        if (!container.querySelector('input')) {
                            container.style.display = 'none';
                        }
                    }
                }
            });
            
            // Brute force approach: apply black text to ALL elements within the slider
            slider.querySelectorAll('*').forEach(el => {
                el.style.setProperty('color', 'black', 'important');
                
                // Try the setAttribute method as well
                el.setAttribute('style', el.getAttribute('style') + '; color: black !important; text-shadow: none !important;');
            });
        });
    } catch (error) {
        console.error("Error in extremeForceSliderLabels:", error);
    }
}

// Function to style download buttons
function styleDownloadButtons() {
    document.querySelectorAll('[data-testid="stDownloadButton"] button').forEach(button => {
        // Apply initial styling
        button.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
        button.style.color = '#4CAF50'; // Green text
        button.style.border = '2px solid #4CAF50';
        button.style.fontWeight = '700';
        button.style.fontSize = '1.1rem';
        button.style.padding = '0.75rem 1.5rem';
        button.style.borderRadius = '8px';
        button.style.transition = 'all 0.3s ease';
        button.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
        
        // Style any spans within the button
        button.querySelectorAll('span').forEach(span => {
            span.style.color = '#4CAF50'; // Ensure text is green
        });
        
        // Add hover effects
        button.addEventListener('mouseenter', () => {
            button.style.backgroundColor = '#4CAF50';
            button.style.color = 'white';
            button.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.2)';
            button.style.transform = 'translateY(-2px)';
            
            // Update spans on hover
            button.querySelectorAll('span').forEach(span => {
                span.style.color = 'white';
            });
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
            button.style.color = '#4CAF50';
            button.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
            button.style.transform = 'translateY(0)';
            
            // Reset spans on hover out
            button.querySelectorAll('span').forEach(span => {
                span.style.color = '#4CAF50';
            });
        });
    });
}

// Main function to call all style functions
function applyAllStyles() {
    styleNavbar();
    applyGradients();
    styleInputsAndPopups();
    forceSelectBoxTextColor();
    styleFormLabels();
    styleSliderHeaders();
    fixStreamlitWidgetText();
    extremeForceSliderLabels();
    styleDownloadButtons(); // Add this call to style download buttons
}

// Apply styles on load and periodically afterward to catch dynamically added elements
document.addEventListener('DOMContentLoaded', () => {
    // Initial styling
    setTimeout(applyAllStyles, 1000);
    
    // Periodic styling to catch dynamically added elements
    setInterval(applyAllStyles, 3000);
}); 