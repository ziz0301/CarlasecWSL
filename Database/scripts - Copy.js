document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.querySelector(".menu-toggle");
	if (!menuToggle) return;
    const nav = document.querySelector("nav");
	if (!nav) return;
    menuToggle.addEventListener("click", function () {
        nav.classList.toggle("active");
    });
});


document.addEventListener("DOMContentLoaded", function () {
	const selector = document.getElementById("data-version");
    // Load initial version
    loadData("data_v1.json");

    // Listen for changes
    selector.addEventListener("change", function () {
        const selectedFile = selector.value;
        loadData(selectedFile);
    });


  // fetchData();
});

	function fetchData() {
		fetch("data.json")
			.then(response => response.json())
			.then(data => {
				loadTacticsAndTechniques(data);
				loadReferences(data.references);
				loadTactics(data.tactics);
				loadTechniques(data.techniques);
			})
			.catch(error => console.error("Error loading data.json:", error));
	}

	function loadTacticsAndTechniques(data){
		const matrixContainer = document.getElementById("matrix-container");
		if (!matrixContainer) return;
		data.tactics.forEach(tactic => {
			let tacticDiv = document.createElement("div");
			tacticDiv.classList.add("tactic");
			tacticDiv.innerHTML = `<b><a href="#" onclick="showPopup('${tactic.ID}', 'tactic')">${tactic.name}</a></b>`;
			
			tactic["technique ID"].forEach(techId => {
				let tech = data.techniques.find(t => t.ID === techId);
				if (tech) {
					let techDiv = document.createElement("div");
					techDiv.classList.add("techniques");
					
					let toggleButton = "";
					if (tech["sub-technique ID"].length > 0) {
						toggleButton = `<button class="toggle-btn" onclick="toggleSubTechniques(event, '${tech.ID}')">[+]</button>`;
					}
					
					techDiv.innerHTML = `${toggleButton} <a href="#" onclick="showPopup('${tech.ID}', 'technique')">${tech.name}</a>`;
					
					let subTechContainer = document.createElement("div");
					subTechContainer.id = `sub-tech-${tech.ID}`;
					subTechContainer.classList.add("sub-techniques");
					
					tech["sub-technique ID"].forEach(subTechId => {
						let subTech = data["sub-techniques"].find(st => st.ID === subTechId);
						if (subTech) {
							let subTechDiv = document.createElement("div");
							subTechDiv.classList.add("sub-techniques-item")
							subTechDiv.innerHTML = `<a href="#" onclick="showPopup('${subTech.ID}', 'sub-technique')">${subTech.name}</a>`;
							subTechContainer.appendChild(subTechDiv);
						}
					});
					
					techDiv.appendChild(subTechContainer);
					tacticDiv.appendChild(techDiv);
				}
			});
			
			matrixContainer.appendChild(tacticDiv);
		});
	}
	
	function loadTactics(tactics){
		const tacticTable = document.getElementById("tactics-table");
		if (!tacticTable) return;
		tacticTable.innerHTML = "";

		tactics.forEach(tactic => {
			let row = document.createElement("tr");
			row.innerHTML = `
				<td>${tactic.ID}</td>
				<td class="clickable"><a href="#" onclick="showPopup('${tactic.ID}', 'tactic')">${tactic.name}</a></td>
				<td>${tactic.short_description || "No description available."}</td>
			`;
			tacticTable.appendChild(row);
		});
	};
	
	function loadTechniques(techniques){
		const techniqueTable = document.getElementById("techniques-table");
		if (!techniqueTable) return;
		techniqueTable.innerHTML = "";

		techniques.forEach(technique => {
			let row = document.createElement("tr");
			row.innerHTML = `
				<td>${technique.ID}</td>
				<td class="clickable"><a href="#" onclick="showPopup('${technique.ID}', 'technique')">${technique.name}</a></td>
				<td>${technique.short_description || "No description available."}</td>
			`;
			techniqueTable.appendChild(row);
		});
	};
	
	function loadReferences(references) {
		const referenceTable = document.getElementById("references-table");
		if (!referenceTable) return;
		
		referenceTable.innerHTML = ""; // Clear previous data

		references.forEach(ref => {
			let row = document.createElement("tr");
			row.innerHTML = `
				<td>${ref.ID}</td>
				<td class="clickable"><a href="#" onclick="showRefPopup(${JSON.stringify(ref).replace(/"/g, '&quot;')})">${ref.name}</a></td>
				<td><a href="${ref.link}" target="_blank">&#128065;</a></td>
			`;
			referenceTable.appendChild(row);
		});
	}

	
    function toggleSubTechniques(event, techID) {
        event.stopPropagation();
        let subTechContainer = document.getElementById(`sub-tech-${techID}`);
        if (subTechContainer.style.display === "none" || subTechContainer.style.display === "") {
            subTechContainer.style.display = "block";
            event.target.textContent = "[-]";
        } else {
            subTechContainer.style.display = "none";
            event.target.textContent = "[+]";
        }
    }
    
    function showPopup(id, type) {
        fetch('data.json')
            .then(response => response.json())
            .then(data => {
                let popupBody = document.getElementById("popup-body");
                let item = (type === "tactic") ? data.tactics.find(t => t.ID === id) : 
                           (type === "technique") ? data.techniques.find(t => t.ID === id) :
                           data["sub-techniques"].find(st => st.ID === id);
                if (!item) return;
                
                let content = `<h2>${item.name}</h2>`;
                content += `<p><i>ID:</i> ${item.ID}</p>`;
				content += `<p><strong>Created:</strong> ${item.created} | <strong>Last Modified:</strong> ${item.last_modified}</p>`;
                content += `<h3>Description:</h3> <p>${item.short_description ? item.short_description
							.replace(/\n/g, "<br><br>")
						    .replace(/\t/g, "&nbsp;&nbsp;&nbsp;&nbsp;")	: "No short description available."}</p>`;

				content += `<p>${item.full_description ? item.full_description
							.replace(/\n/g, "<br><br>")  
							.replace(/\t/g, "&nbsp;&nbsp;&nbsp;&nbsp;") : "No full description available."}</p>`;
                
                if (type === "tactic" && item["technique ID"].length > 0) {
                    content += `<h3>Techniques</h3>`;
                    content += `<table border="1" width="100%">
                        <tr><th>ID</th><th>Name</th><th>Description</th></tr>`;
                    item["technique ID"].forEach(techId => {
                        let tech = data.techniques.find(t => t.ID === techId);
                        if (tech) {
                            content += `<tr><td>${tech.ID}</td>
                                        <td><a href="#" onclick="showPopup('${tech.ID}', 'technique')">${tech.name}</a></td>
                                        <td>${tech.short_description}</td></tr>`;
                            tech["sub-technique ID"].forEach(subTechId => {
                                let subTech = data["sub-techniques"].find(st => st.ID === subTechId);
                                if (subTech) {
                                    content += `<tr class="sub-technique-row">
                                                <td>${subTech.ID}</td>
												<td><a href="#" onclick="showPopup('${subTech.ID}', 'sub-technique')">${subTech.name}</a></td>
                                                <td>${subTech.short_description}</td></tr>`;
                                }
                            });
                        }
                    });
                    content += `</table>`;
                }
                
                if (type === "technique") {
                    if (item["sub-technique ID"].length > 0) {
                        content += `<h3>Sub-Techniques</h3><table border="1" width="100%">
                            <tr><th>ID</th><th>Name</th><th>Description</th></tr>`;
                        item["sub-technique ID"].forEach(subTechId => {
                            let subTech = data["sub-techniques"].find(st => st.ID === subTechId);
                            if (subTech) {
                                content += `<tr class="sub-technique-row">
                                            <td>${subTech.ID}</td>
                                            <td><a href="#" onclick="showPopup('${subTech.ID}', 'sub-technique')">${subTech.name}</a></td>
                                            <td>${subTech.short_description}</td></tr>`;
                            }
                        });
                        content += `</table>`;
                    }
                    
                    if (item["example"].length > 0) {
                        content += `<h3>Examples</h3><table border="1" width="100%">
                            <tr><th>Reference</th><th>Description</th></tr>`;
                        item["example"].forEach(ex => {
                            let ref = data.references.find(r => r.ID === ex["reference ID"]);
                            let refLink = ref ? `<a href='${ref.link}' target='_blank'>${ref.name}</a>` : "Unknown Reference";
                            content += `<tr><td class="examref">${refLink}</td><td>${ex.description}</td></tr>`;
                        });
                        content += `</table>`;
                    }
                    
                    if (item["mitigation ID"].length > 0) {
                        content += `<h3>Mitigations</h3><table border="1" width="100%">
                            <tr><th>ID</th><th>Name</th><th>Description</th><th>Reference</th></tr>`;
                        item["mitigation ID"].forEach(mitId => {
                            let mit = data.mitigations.find(m => m.ID === mitId);
                            let refLinks = mit["reference ID"].map(refId => {
                                let ref = data.references.find(r => r.ID === refId);
                                return ref ? `<a href='${ref.link}' target='_blank'>${ref.name}</a>` : "Unknown Reference";
                            }).join(", ");
                            content += `<tr><td>${mit.ID}</td><td>${mit.name}</td><td>${mit.description}</td><td>${refLinks}</td></tr>`;
                        });
                        content += `</table>`;
                    }
                    
                    if (item["reference ID"]?.length > 0) {
						content += `<h3>References</h3><table border="1" width="100%">
							<tr><th>ID</th><th>Name</th><th>Link</th></tr>`;
						item["reference ID"].forEach(refId => {
							let ref = data.references.find(r => r.ID === refId);
							console.log(ref);
							if (ref) {
								content += `<tr>
											<td>${ref.ID}</td>
											<td class="clickable"><a href="#" onclick="showRefPopup(${JSON.stringify(ref).replace(/"/g, '&quot;')})">${ref.name}</a></td>
											<td><a href="${ref.link}" target="_blank">&#128065;</a></td>
											</tr>`;
							}
						});
						content += `</table>`;
					} else {
						content += `<p><h3>References:</h3> No references available.</p>`;
					}
                }
				if (type === "sub-technique") {
                    if (item["example"]?.length > 0) {
                        content += `<h3>Examples</h3><table border="1" width="100%">
                            <tr><th>Reference</th><th>Description</th></tr>`;
                        item["example"].forEach(ex => {
                            let ref = data.references.find(r => r.ID === ex["reference ID"]);
                            let refLink = ref ? `<a href='${ref.link}' target='_blank'>${ref.name}</a>` : "Unknown Reference";
                            content += `<tr><td class="examref">${refLink}</td><td>${ex.description}</td></tr>`;
                        });
                        content += `</table>`;
                    }
                    
                    if (item["mitigation ID"]?.length > 0) {
                        content += `<h3>Mitigations</h3><table border="1" width="100%">
                            <tr><th>ID</th><th>Name</th><th>Description</th><th>Reference</th></tr>`;
                        item["mitigation ID"].forEach(mitId => {
                            let mit = data.mitigations.find(m => m.ID === mitId);
                            let refLinks = mit["reference ID"].map(refId => {
                                let ref = data.references.find(r => r.ID === refId);
                                return ref ? `<a href='${ref.link}' target='_blank'>${ref.name}</a>` : "Unknown Reference";
                            }).join(", ");
                            content += `<tr><td>${mit.ID}</td><td>${mit.name}</td><td>${mit.description}</td><td>${refLinks}</td></tr>`;
                        });
                        content += `</table>`;
                    }
                    
                    if (item["reference ID"]?.length > 0) {
						content += `<h3>References</h3><table border="1" width="100%">
							<tr><th>ID</th><th>Name</th><th>Link</th></tr>`;
						item["reference ID"].forEach(refId => {
							let ref = data.references.find(r => r.ID === refId);
							if (ref) {
								content += `<tr>
											<td>${ref.ID}</td>
											<td class="clickable"><a href="#" onclick="showRefPopup(${JSON.stringify(ref).replace(/"/g, '&quot;')})">${ref.name}</a></td>
											<td><a href="${ref.link}" target="_blank">&#128065;</a></td>
											</tr>`;
							}
						});
						content += `</table>`;
					} else {
						content += `<p><h3>References:</h3> No references available.</p>`;
					}
                }
                
                document.getElementById("popup").style.display = "block";
                popupBody.innerHTML = content;
            });
    }
    
   
	function handleReferenceClick(element) {
		let ref = JSON.parse(element.getAttribute("data-ref"));
		//let ref = JSON.parse(decodeURIComponent(element.getAttribute("data-ref")));
		showRefPopup(ref);
	}

		
	function showRefPopup(ref) {
		const popup = document.getElementById("popup");
		const popupBody = document.getElementById("popup-body");
		let refContent = `<h3>${ref.name}</h3>
                      <p>${ref.cite}</p>
                      <a href="${ref.link}" target="_blank">Open link</a>`;    
		let description = ref.description ? ref.description.replace(/\n/g, "<br><br>").replace(/\t/g, "&nbsp;&nbsp;&nbsp;&nbsp;"): "No description available.";
    
		refContent += `<h3>Description:</h3> <p>${description}</p>`;
		popupBody.innerHTML = refContent;
		popup.style.display = "block";
	}

	
	function closePopup() {
        document.getElementById("popup").style.display = "none";
    }
	
window.showPopup = showPopup;
window.closePopup = closePopup;
window.toggleSubTechniques = toggleSubTechniques;
	
	
	
	
	
	
	
	
