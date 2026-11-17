/**
 * Main Application Logic for Student Management System
 */

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

const App = {
    currentTab: 'dashboard',
    departments: [],
    courses: [],
    students: [],
    deptChart: null,

    init() {
        this.setupNavigation();
        this.setupEventListeners();
        this.loadInitialData();
        this.setupSearch();
    },

    // --- Navigation & Tabs ---
    setupNavigation() {
        const navLinks = document.querySelectorAll('[data-tab-target]');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.getAttribute('data-tab-target');
                this.switchTab(target);
            });
        });
    },

    switchTab(tabId) {
        this.currentTab = tabId;

        // Update active class on nav links
        document.querySelectorAll('[data-tab-target]').forEach(el => {
            if (el.getAttribute('data-tab-target') === tabId) {
                el.classList.add('bg-indigo-700', 'text-white');
                el.classList.remove('text-indigo-100', 'hover:bg-indigo-800');
            } else {
                el.classList.remove('bg-indigo-700', 'text-white');
                el.classList.add('text-indigo-100', 'hover:bg-indigo-800');
            }
        });

        // Toggle sections
        document.querySelectorAll('.tab-section').forEach(sec => {
            if (sec.id === `section-${tabId}`) {
                sec.classList.remove('hidden');
            } else {
                sec.classList.add('hidden');
            }
        });

        // Trigger tab-specific refresh
        if (tabId === 'dashboard') this.loadDashboard();
        if (tabId === 'students') this.loadStudents();
        if (tabId === 'courses') this.loadCourses();
        if (tabId === 'departments') this.loadDepartments();
        if (tabId === 'enrollments') this.loadEnrollments();
        if (tabId === 'attendance') this.loadAttendance();
        if (tabId === 'settings') this.loadSettings();
    },

    // --- Initial Data Pre-load ---
    async loadInitialData() {
        await Promise.all([
            this.fetchReferenceData(),
            this.loadDashboard(),
            this.loadSystemStatus()
        ]);
    },

    async fetchReferenceData() {
        try {
            const [depts, crs] = await Promise.all([
                API.getDepartments(),
                API.getCourses()
            ]);
            this.departments = depts;
            this.courses = crs;
            this.populateDropdowns();
        } catch (error) {
            console.error('Failed to load reference metadata:', error);
        }
    },

    populateDropdowns() {
        // Department dropdowns
        const deptSelects = [
            'student-filter-dept',
            'student-form-dept',
            'course-form-dept',
            'course-filter-dept'
        ];
        deptSelects.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            const currentVal = el.value;
            const isFilter = id.includes('filter');
            el.innerHTML = isFilter ? '<option value="">All Departments</option>' : '<option value="">Select Department</option>';
            this.departments.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d.id;
                opt.textContent = `${d.code} - ${d.name}`;
                el.appendChild(opt);
            });
            if (currentVal) el.value = currentVal;
        });

        // Course dropdowns
        const courseSelects = [
            'enrollment-form-course',
            'attendance-form-course',
            'attendance-filter-course'
        ];
        courseSelects.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            const isFilter = id.includes('filter');
            el.innerHTML = isFilter ? '<option value="">All Courses</option>' : '<option value="">Select Course</option>';
            this.courses.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = `${c.code} - ${c.name}`;
                el.appendChild(opt);
            });
        });
    },

    // --- Search Setup ---
    setupSearch() {
        const globalSearch = document.getElementById('global-search');
        if (globalSearch) {
            let timeout = null;
            globalSearch.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    const query = e.target.value.trim();
                    if (this.currentTab !== 'students') {
                        this.switchTab('students');
                    }
                    const searchInput = document.getElementById('student-search-input');
                    if (searchInput) {
                        searchInput.value = query;
                        this.loadStudents();
                    }
                }, 300);
            });
        }

        const studentSearch = document.getElementById('student-search-input');
        if (studentSearch) {
            let timeout = null;
            studentSearch.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => this.loadStudents(), 300);
            });
        }

        ['student-filter-dept', 'student-filter-status', 'student-filter-semester'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('change', () => this.loadStudents());
        });
    },

    // --- Dashboard Module ---
    async loadDashboard() {
        try {
            const stats = await API.getStats();
            document.getElementById('stat-total-students').textContent = stats.total_students;
            document.getElementById('stat-active-students').textContent = stats.active_students;
            document.getElementById('stat-total-courses').textContent = stats.total_courses;
            document.getElementById('stat-avg-gpa').textContent = stats.average_gpa ? stats.average_gpa.toFixed(2) : '0.00';
            document.getElementById('stat-total-departments').textContent = stats.total_departments;

            this.renderDepartmentChart(stats.department_distribution);
            this.loadRecentStudents();
        } catch (error) {
            console.error('Failed to load dashboard statistics:', error);
            this.showToast('Could not load statistics', 'error');
        }
    },

    renderDepartmentChart(distribution) {
        const ctx = document.getElementById('deptDistributionChart');
        if (!ctx) return;

        if (this.deptChart) {
            this.deptChart.destroy();
        }

        const labels = distribution.map(d => d.code);
        const data = distribution.map(d => d.student_count);
        const backgroundColors = [
            '#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'
        ];

        this.deptChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: backgroundColors.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, font: { family: 'Inter', size: 12 } }
                    }
                },
                cutout: '70%'
            }
        });
    },

    async loadRecentStudents() {
        try {
            const students = await API.getStudents({ limit: 5 });
            const tbody = document.getElementById('recent-students-tbody');
            if (!tbody) return;

            if (students.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-gray-500">No students found.</td></tr>`;
                return;
            }

            tbody.innerHTML = students.map(s => `
                <tr class="hover:bg-gray-50 border-b border-gray-100 transition">
                    <td class="py-3 px-4 font-medium text-gray-900">${this.escape(s.roll_number)}</td>
                    <td class="py-3 px-4">
                        <div class="font-medium text-gray-900">${this.escape(s.full_name)}</div>
                        <div class="text-xs text-gray-500">${this.escape(s.email)}</div>
                    </td>
                    <td class="py-3 px-4"><span class="px-2 py-1 text-xs font-semibold rounded-full bg-indigo-50 text-indigo-700">${this.escape(s.department_code || 'N/A')}</span></td>
                    <td class="py-3 px-4">${this.renderStatusBadge(s.status)}</td>
                    <td class="py-3 px-4 text-right">
                        <button onclick="App.viewStudentDetail(${s.id})" class="text-indigo-600 hover:text-indigo-900 text-sm font-medium">View</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error loading recent students:', error);
        }
    },

    // --- Students Module ---
    async loadStudents() {
        const search = document.getElementById('student-search-input')?.value.trim();
        const deptId = document.getElementById('student-filter-dept')?.value;
        const status = document.getElementById('student-filter-status')?.value;
        const semester = document.getElementById('student-filter-semester')?.value;

        try {
            const students = await API.getStudents({
                search: search || null,
                department_id: deptId || null,
                status: status || null,
                semester: semester || null,
                limit: 200
            });
            this.students = students;
            this.renderStudentsTable(students);
        } catch (error) {
            this.showToast('Failed to load students: ' + error.message, 'error');
        }
    },

    renderStudentsTable(students) {
        const tbody = document.getElementById('students-table-tbody');
        const countBadge = document.getElementById('students-count-badge');
        if (countBadge) countBadge.textContent = `${students.length} Students`;
        if (!tbody) return;

        if (students.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="py-12 text-center text-gray-500">
                        <i class="fas fa-user-slash text-4xl mb-3 text-gray-300"></i>
                        <p class="text-base font-medium">No students match your criteria</p>
                        <p class="text-sm text-gray-400 mt-1">Try clearing filters or adding a new student.</p>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = students.map(s => `
            <tr class="hover:bg-slate-50 border-b border-gray-100 transition">
                <td class="py-3 px-4 font-semibold text-indigo-600">${this.escape(s.roll_number)}</td>
                <td class="py-3 px-4">
                    <div class="font-medium text-gray-900">${this.escape(s.full_name)}</div>
                    <div class="text-xs text-gray-500"><i class="far fa-envelope mr-1"></i>${this.escape(s.email)}</div>
                    ${s.phone ? `<div class="text-xs text-gray-400"><i class="fas fa-phone-alt mr-1"></i>${this.escape(s.phone)}</div>` : ''}
                </td>
                <td class="py-3 px-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                        ${this.escape(s.department_code || 'N/A')}
                    </span>
                    <div class="text-xs text-gray-500 mt-0.5">${this.escape(s.department_name || '')}</div>
                </td>
                <td class="py-3 px-4 text-sm text-gray-700">
                    <div>Sem ${s.semester}</div>
                    <div class="text-xs text-gray-400">Year ${s.year_of_study}</div>
                </td>
                <td class="py-3 px-4">
                    ${this.renderStatusBadge(s.status)}
                </td>
                <td class="py-3 px-4 text-sm font-semibold ${s.gpa && s.gpa >= 3.5 ? 'text-emerald-600' : 'text-gray-700'}">
                    ${s.gpa ? s.gpa.toFixed(2) : '<span class="text-gray-400 font-normal">N/A</span>'}
                </td>
                <td class="py-3 px-4 text-right space-x-2">
                    <button onclick="App.viewStudentDetail(${s.id})" title="View Profile" class="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded transition">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="App.openEditStudentModal(${s.id})" title="Edit Student" class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="App.confirmDeleteStudent(${s.id}, '${this.escape(s.full_name)}')" title="Delete Student" class="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    },

    openAddStudentModal() {
        document.getElementById('student-modal-title').textContent = 'Register New Student';
        document.getElementById('student-form').reset();
        document.getElementById('student-form-id').value = '';
        document.getElementById('student-form-enrollment-date').value = new Date().toISOString().split('T')[0];
        this.openModal('student-modal');
    },

    async openEditStudentModal(id) {
        try {
            const student = await API.getStudent(id);
            document.getElementById('student-modal-title').textContent = `Edit Student: ${student.full_name}`;
            document.getElementById('student-form-id').value = student.id;
            document.getElementById('student-form-roll').value = student.roll_number;
            document.getElementById('student-form-first-name').value = student.first_name;
            document.getElementById('student-form-last-name').value = student.last_name;
            document.getElementById('student-form-email').value = student.email;
            document.getElementById('student-form-phone').value = student.phone || '';
            document.getElementById('student-form-dob').value = student.date_of_birth || '';
            document.getElementById('student-form-gender').value = student.gender || 'Other';
            document.getElementById('student-form-dept').value = student.department_id;
            document.getElementById('student-form-year').value = student.year_of_study;
            document.getElementById('student-form-semester').value = student.semester;
            document.getElementById('student-form-status').value = student.status;
            document.getElementById('student-form-enrollment-date').value = student.enrollment_date;
            document.getElementById('student-form-address').value = student.address || '';
            this.openModal('student-modal');
        } catch (error) {
            this.showToast('Failed to load student: ' + error.message, 'error');
        }
    },

    async handleStudentFormSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('student-form-id').value;
        const data = {
            roll_number: document.getElementById('student-form-roll').value.trim(),
            first_name: document.getElementById('student-form-first-name').value.trim(),
            last_name: document.getElementById('student-form-last-name').value.trim(),
            email: document.getElementById('student-form-email').value.trim(),
            phone: document.getElementById('student-form-phone').value.trim() || null,
            date_of_birth: document.getElementById('student-form-dob').value || null,
            gender: document.getElementById('student-form-gender').value,
            department_id: parseInt(document.getElementById('student-form-dept').value),
            year_of_study: parseInt(document.getElementById('student-form-year').value),
            semester: parseInt(document.getElementById('student-form-semester').value),
            status: document.getElementById('student-form-status').value,
            enrollment_date: document.getElementById('student-form-enrollment-date').value,
            address: document.getElementById('student-form-address').value.trim() || null
        };

        try {
            if (id) {
                await API.updateStudent(id, data);
                this.showToast('Student updated successfully!', 'success');
            } else {
                await API.createStudent(data);
                this.showToast('Student registered successfully!', 'success');
            }
            this.closeModal('student-modal');
            this.loadStudents();
            this.loadDashboard();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    confirmDeleteStudent(id, name) {
        this.openConfirmModal({
            title: 'Delete Student',
            message: `Are you sure you want to permanently delete student <strong>${name}</strong>? All associated enrollment and attendance records will be removed.`,
            confirmText: 'Delete Student',
            confirmClass: 'bg-red-600 hover:bg-red-700',
            onConfirm: async () => {
                try {
                    await API.deleteStudent(id);
                    this.showToast('Student deleted successfully', 'success');
                    this.loadStudents();
                    this.loadDashboard();
                } catch (error) {
                    this.showToast('Failed to delete student: ' + error.message, 'error');
                }
            }
        });
    },

    async viewStudentDetail(id) {
        try {
            const s = await API.getStudentDetail(id);
            document.getElementById('detail-full-name').textContent = s.full_name;
            document.getElementById('detail-roll').textContent = s.roll_number;
            document.getElementById('detail-dept').textContent = `${s.department_code} - ${s.department_name}`;
            document.getElementById('detail-status').innerHTML = this.renderStatusBadge(s.status);
            document.getElementById('detail-email').textContent = s.email;
            document.getElementById('detail-phone').textContent = s.phone || 'N/A';
            document.getElementById('detail-gender').textContent = s.gender;
            document.getElementById('detail-dob').textContent = s.date_of_birth || 'N/A';
            document.getElementById('detail-address').textContent = s.address || 'N/A';
            document.getElementById('detail-enrolled-date').textContent = s.enrollment_date;
            document.getElementById('detail-year-sem').textContent = `Year ${s.year_of_study}, Semester ${s.semester}`;
            document.getElementById('detail-gpa').textContent = s.gpa ? s.gpa.toFixed(2) : 'N/A';
            
            // Attendance percentage
            const attRate = s.attendance_percentage !== null ? `${s.attendance_percentage}%` : 'N/A';
            document.getElementById('detail-attendance-rate').textContent = attRate;

            // Render Enrolled Courses
            const coursesContainer = document.getElementById('detail-courses-list');
            if (s.enrollments && s.enrollments.length > 0) {
                coursesContainer.innerHTML = s.enrollments.map(e => `
                    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100 mb-2">
                        <div>
                            <span class="font-semibold text-gray-900">${this.escape(e.course_code)}</span> - ${this.escape(e.course_name)}
                            <div class="text-xs text-gray-500">${this.escape(e.semester_name)} • ${e.course_credits} Credits</div>
                        </div>
                        <div class="text-right">
                            <span class="px-2 py-0.5 text-xs font-bold rounded ${e.grade ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-200 text-gray-700'}">
                                ${e.grade ? `Grade: ${e.grade} (${e.grade_point})` : 'In Progress'}
                            </span>
                            <div class="text-xs text-gray-400 mt-0.5">${e.status}</div>
                        </div>
                    </div>
                `).join('');
            } else {
                coursesContainer.innerHTML = `<p class="text-sm text-gray-500 italic">No course enrollments found.</p>`;
            }

            // Render Attendance logs
            const attendanceContainer = document.getElementById('detail-attendance-list');
            if (s.attendance_records && s.attendance_records.length > 0) {
                attendanceContainer.innerHTML = s.attendance_records.map(a => `
                    <div class="flex items-center justify-between py-2 border-b border-gray-100 text-sm">
                        <div>
                            <span class="font-medium text-gray-800">${this.escape(a.course_code)}</span>
                            <span class="text-xs text-gray-400 ml-2">${a.date}</span>
                        </div>
                        <div>
                            ${this.renderAttendanceBadge(a.status)}
                        </div>
                    </div>
                `).join('');
            } else {
                attendanceContainer.innerHTML = `<p class="text-sm text-gray-500 italic">No attendance records logged.</p>`;
            }

            this.openModal('student-detail-modal');
        } catch (error) {
            this.showToast('Failed to load student details: ' + error.message, 'error');
        }
    },

    exportStudentsCSV() {
        window.location.href = '/api/students/export/csv';
        this.showToast('Downloading students CSV...', 'info');
    },

    // --- Courses Module ---
    async loadCourses() {
        const deptId = document.getElementById('course-filter-dept')?.value;
        try {
            const courses = await API.getCourses(deptId || null);
            this.courses = courses;
            this.renderCoursesTable(courses);
        } catch (error) {
            this.showToast('Failed to load courses: ' + error.message, 'error');
        }
    },

    renderCoursesTable(courses) {
        const tbody = document.getElementById('courses-table-tbody');
        if (!tbody) return;

        if (courses.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-gray-500">No courses found.</td></tr>`;
            return;
        }

        tbody.innerHTML = courses.map(c => `
            <tr class="hover:bg-slate-50 border-b border-gray-100 transition">
                <td class="py-3 px-4 font-semibold text-indigo-600">${this.escape(c.code)}</td>
                <td class="py-3 px-4">
                    <div class="font-medium text-gray-900">${this.escape(c.name)}</div>
                    ${c.description ? `<div class="text-xs text-gray-500 truncate max-w-md">${this.escape(c.description)}</div>` : ''}
                </td>
                <td class="py-3 px-4"><span class="px-2 py-1 text-xs font-semibold rounded bg-amber-100 text-amber-800">${c.credits} Credits</span></td>
                <td class="py-3 px-4 text-sm text-gray-700">${this.escape(c.department_name || 'N/A')}</td>
                <td class="py-3 px-4 text-sm text-gray-700">${this.escape(c.instructor || 'Unassigned')}</td>
                <td class="py-3 px-4 text-right space-x-2">
                    <button onclick="App.openEditCourseModal(${c.id})" class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition"><i class="fas fa-edit"></i></button>
                    <button onclick="App.confirmDeleteCourse(${c.id}, '${this.escape(c.name)}')" class="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition"><i class="fas fa-trash-alt"></i></button>
                </td>
            </tr>
        `).join('');
    },

    openAddCourseModal() {
        document.getElementById('course-modal-title').textContent = 'Add New Course';
        document.getElementById('course-form').reset();
        document.getElementById('course-form-id').value = '';
        this.openModal('course-modal');
    },

    async openEditCourseModal(id) {
        const course = this.courses.find(c => c.id === id);
        if (!course) return;
        document.getElementById('course-modal-title').textContent = `Edit Course: ${course.code}`;
        document.getElementById('course-form-id').value = course.id;
        document.getElementById('course-form-code').value = course.code;
        document.getElementById('course-form-name').value = course.name;
        document.getElementById('course-form-credits').value = course.credits;
        document.getElementById('course-form-dept').value = course.department_id;
        document.getElementById('course-form-instructor').value = course.instructor || '';
        document.getElementById('course-form-desc').value = course.description || '';
        this.openModal('course-modal');
    },

    async handleCourseFormSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('course-form-id').value;
        const data = {
            code: document.getElementById('course-form-code').value.trim(),
            name: document.getElementById('course-form-name').value.trim(),
            credits: parseInt(document.getElementById('course-form-credits').value),
            department_id: parseInt(document.getElementById('course-form-dept').value),
            instructor: document.getElementById('course-form-instructor').value.trim() || null,
            description: document.getElementById('course-form-desc').value.trim() || null
        };

        try {
            if (id) {
                await API.updateCourse(id, data);
                this.showToast('Course updated successfully!', 'success');
            } else {
                await API.createCourse(data);
                this.showToast('Course created successfully!', 'success');
            }
            this.closeModal('course-modal');
            await this.fetchReferenceData();
            this.loadCourses();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    confirmDeleteCourse(id, name) {
        this.openConfirmModal({
            title: 'Delete Course',
            message: `Are you sure you want to delete course <strong>${name}</strong>?`,
            confirmText: 'Delete Course',
            confirmClass: 'bg-red-600 hover:bg-red-700',
            onConfirm: async () => {
                try {
                    await API.deleteCourse(id);
                    this.showToast('Course deleted successfully', 'success');
                    await this.fetchReferenceData();
                    this.loadCourses();
                } catch (error) {
                    this.showToast('Failed to delete course: ' + error.message, 'error');
                }
            }
        });
    },

    // --- Departments Module ---
    async loadDepartments() {
        try {
            const depts = await API.getDepartments();
            this.departments = depts;
            this.renderDepartmentsGrid(depts);
        } catch (error) {
            this.showToast('Failed to load departments: ' + error.message, 'error');
        }
    },

    renderDepartmentsGrid(departments) {
        const container = document.getElementById('departments-grid');
        if (!container) return;

        if (departments.length === 0) {
            container.innerHTML = `<div class="col-span-full py-8 text-center text-gray-500">No departments found.</div>`;
            return;
        }

        container.innerHTML = departments.map(d => `
            <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition">
                <div class="flex items-start justify-between">
                    <div>
                        <span class="px-2.5 py-1 text-xs font-bold rounded-lg bg-indigo-50 text-indigo-700 uppercase tracking-wider">${this.escape(d.code)}</span>
                        <h3 class="text-lg font-bold text-gray-900 mt-2">${this.escape(d.name)}</h3>
                    </div>
                    <div class="flex space-x-1">
                        <button onclick="App.openEditDeptModal(${d.id})" class="p-1 text-gray-400 hover:text-blue-600"><i class="fas fa-edit"></i></button>
                        <button onclick="App.confirmDeleteDept(${d.id}, '${this.escape(d.name)}')" class="p-1 text-gray-400 hover:text-red-600"><i class="fas fa-trash-alt"></i></button>
                    </div>
                </div>
                <p class="text-sm text-gray-500 mt-2 line-clamp-2">${this.escape(d.description || 'No description provided.')}</p>
                <div class="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                    <div><i class="fas fa-user-tie mr-1 text-gray-400"></i>HOD: <span class="font-medium text-gray-700">${this.escape(d.head_of_department || 'N/A')}</span></div>
                    <div class="flex space-x-3">
                        <span><i class="fas fa-user-graduate mr-1 text-indigo-500"></i><strong>${d.student_count}</strong> Students</span>
                        <span><i class="fas fa-book mr-1 text-emerald-500"></i><strong>${d.course_count}</strong> Courses</span>
                    </div>
                </div>
            </div>
        `).join('');
    },

    openAddDeptModal() {
        document.getElementById('dept-modal-title').textContent = 'Add Department';
        document.getElementById('dept-form').reset();
        document.getElementById('dept-form-id').value = '';
        this.openModal('dept-modal');
    },

    openEditDeptModal(id) {
        const dept = this.departments.find(d => d.id === id);
        if (!dept) return;
        document.getElementById('dept-modal-title').textContent = `Edit Department: ${dept.code}`;
        document.getElementById('dept-form-id').value = dept.id;
        document.getElementById('dept-form-code').value = dept.code;
        document.getElementById('dept-form-name').value = dept.name;
        document.getElementById('dept-form-hod').value = dept.head_of_department || '';
        document.getElementById('dept-form-desc').value = dept.description || '';
        this.openModal('dept-modal');
    },

    async handleDeptFormSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('dept-form-id').value;
        const data = {
            code: document.getElementById('dept-form-code').value.trim(),
            name: document.getElementById('dept-form-name').value.trim(),
            head_of_department: document.getElementById('dept-form-hod').value.trim() || null,
            description: document.getElementById('dept-form-desc').value.trim() || null
        };

        try {
            if (id) {
                await API.updateDepartment(id, data);
                this.showToast('Department updated successfully!', 'success');
            } else {
                await API.createDepartment(data);
                this.showToast('Department created successfully!', 'success');
            }
            this.closeModal('dept-modal');
            await this.fetchReferenceData();
            this.loadDepartments();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    confirmDeleteDept(id, name) {
        this.openConfirmModal({
            title: 'Delete Department',
            message: `Are you sure you want to delete department <strong>${name}</strong>? It cannot be deleted if active students exist.`,
            confirmText: 'Delete Department',
            confirmClass: 'bg-red-600 hover:bg-red-700',
            onConfirm: async () => {
                try {
                    await API.deleteDepartment(id);
                    this.showToast('Department deleted successfully', 'success');
                    await this.fetchReferenceData();
                    this.loadDepartments();
                } catch (error) {
                    this.showToast('Failed to delete: ' + error.message, 'error');
                }
            }
        });
    },

    // --- Enrollments & Grades Module ---
    async loadEnrollments() {
        try {
            const enrollments = await API.getEnrollments();
            this.renderEnrollmentsTable(enrollments);
        } catch (error) {
            this.showToast('Failed to load enrollments: ' + error.message, 'error');
        }
    },

    renderEnrollmentsTable(enrollments) {
        const tbody = document.getElementById('enrollments-table-tbody');
        if (!tbody) return;

        if (enrollments.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-gray-500">No enrollment records found.</td></tr>`;
            return;
        }

        tbody.innerHTML = enrollments.map(e => `
            <tr class="hover:bg-slate-50 border-b border-gray-100 transition">
                <td class="py-3 px-4">
                    <div class="font-semibold text-gray-900">${this.escape(e.student_name)}</div>
                    <div class="text-xs text-indigo-600 font-mono">${this.escape(e.student_roll)}</div>
                </td>
                <td class="py-3 px-4">
                    <span class="font-medium text-gray-800">${this.escape(e.course_code)}</span> - ${this.escape(e.course_name)}
                </td>
                <td class="py-3 px-4 text-sm text-gray-600">${this.escape(e.semester_name)}</td>
                <td class="py-3 px-4">
                    <span class="px-2.5 py-1 text-xs font-bold rounded ${e.grade ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-600'}">
                        ${e.grade ? `${e.grade} (${e.grade_point})` : 'Pending'}
                    </span>
                </td>
                <td class="py-3 px-4">
                    <span class="px-2 py-0.5 text-xs font-semibold rounded-full ${e.status === 'Completed' ? 'bg-green-100 text-green-800' : e.status === 'Enrolled' ? 'bg-blue-100 text-blue-800' : 'bg-rose-100 text-rose-800'}">
                        ${e.status}
                    </span>
                </td>
                <td class="py-3 px-4 text-xs text-gray-400">${e.enrolled_date}</td>
                <td class="py-3 px-4 text-right space-x-2">
                    <button onclick="App.openGradeModal(${e.id}, '${e.grade || ''}', '${e.status}')" title="Assign / Update Grade" class="px-2 py-1 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded text-xs font-medium transition">
                        <i class="fas fa-award mr-1"></i>Grade
                    </button>
                    <button onclick="App.confirmDeleteEnrollment(${e.id})" title="Remove Enrollment" class="p-1.5 text-gray-400 hover:text-red-600 rounded transition">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    },

    async openEnrollStudentModal() {
        document.getElementById('enrollment-form').reset();
        document.getElementById('enrollment-form-date').value = new Date().toISOString().split('T')[0];
        
        const deptBadge = document.getElementById('enrollment-form-dept-badge');
        if (deptBadge) deptBadge.textContent = '';
        const hintEl = document.getElementById('enrollment-form-hint');
        if (hintEl) hintEl.classList.add('hidden');

        // Populate Student dropdown with active students only
        const studentSelect = document.getElementById('enrollment-form-student');
        try {
            const students = await API.getStudents({ limit: 500, status: 'Active' });
            this.allActiveStudents = students;
            studentSelect.innerHTML = '<option value="">Select Active Student</option>' + students.map(s => `
                <option value="${s.id}">${this.escape(s.roll_number)} - ${this.escape(s.full_name)} (${this.escape(s.department_code || 'Dept')})</option>
            `).join('');
            
            this.populateEnrollmentCourses(this.courses);
        } catch (error) {
            console.error('Error loading students for enrollment:', error);
        }
        this.openModal('enrollment-modal');
    },

    populateEnrollmentCourses(coursesList) {
        const courseSelect = document.getElementById('enrollment-form-course');
        if (!courseSelect) return;
        courseSelect.innerHTML = '<option value="">Select Course</option>' + coursesList.map(c => `
            <option value="${c.id}">${this.escape(c.code)} - ${this.escape(c.name)} (${this.escape(c.department_name || '')})</option>
        `).join('');
    },

    onEnrollStudentChange(studentId) {
        const courseSelect = document.getElementById('enrollment-form-course');
        const deptBadge = document.getElementById('enrollment-form-dept-badge');
        const hintEl = document.getElementById('enrollment-form-hint');
        if (!courseSelect) return;

        if (!studentId) {
            if (deptBadge) deptBadge.textContent = '';
            if (hintEl) hintEl.classList.add('hidden');
            this.populateEnrollmentCourses(this.courses);
            return;
        }

        const student = this.allActiveStudents?.find(s => s.id == studentId);
        if (!student) return;

        if (deptBadge) deptBadge.textContent = `Dept: ${student.department_code || ''}`;
        const matchingCourses = this.courses.filter(c => c.department_id === student.department_id);

        if (matchingCourses.length === 0) {
            courseSelect.innerHTML = '<option value="">No courses available in this department</option>';
            if (hintEl) {
                hintEl.textContent = `No courses found in ${student.department_name}.`;
                hintEl.classList.remove('hidden');
            }
        } else {
            courseSelect.innerHTML = '<option value="">Select Department Course</option>' + matchingCourses.map(c => `
                <option value="${c.id}">${this.escape(c.code)} - ${this.escape(c.name)} (${c.credits} Credits)</option>
            `).join('');
            if (hintEl) hintEl.classList.add('hidden');
        }
    },

    async handleEnrollmentFormSubmit(e) {
        e.preventDefault();
        const data = {
            student_id: parseInt(document.getElementById('enrollment-form-student').value),
            course_id: parseInt(document.getElementById('enrollment-form-course').value),
            semester_name: document.getElementById('enrollment-form-semester').value.trim(),
            grade: document.getElementById('enrollment-form-grade').value.trim() || null,
            status: document.getElementById('enrollment-form-status').value,
            enrolled_date: document.getElementById('enrollment-form-date').value
        };

        try {
            await API.createEnrollment(data);
            this.showToast('Student enrolled successfully!', 'success');
            this.closeModal('enrollment-modal');
            this.loadEnrollments();
            this.loadDashboard();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    openGradeModal(enrollmentId, currentGrade, currentStatus) {
        document.getElementById('grade-form-id').value = enrollmentId;
        document.getElementById('grade-form-grade').value = currentGrade || '';
        document.getElementById('grade-form-status').value = currentStatus || 'Enrolled';
        this.openModal('grade-modal');
    },

    async handleGradeFormSubmit(e) {
        e.preventDefault();
        const id = document.getElementById('grade-form-id').value;
        const gradeVal = document.getElementById('grade-form-grade').value.trim();
        const statusVal = document.getElementById('grade-form-status').value;

        const data = {
            grade: gradeVal || null,
            status: statusVal
        };

        try {
            await API.updateEnrollment(id, data);
            this.showToast('Grade updated successfully!', 'success');
            this.closeModal('grade-modal');
            this.loadEnrollments();
            this.loadDashboard();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    confirmDeleteEnrollment(id) {
        this.openConfirmModal({
            title: 'Remove Enrollment',
            message: 'Are you sure you want to remove this course enrollment record?',
            confirmText: 'Remove',
            confirmClass: 'bg-red-600 hover:bg-red-700',
            onConfirm: async () => {
                try {
                    await API.deleteEnrollment(id);
                    this.showToast('Enrollment removed', 'success');
                    this.loadEnrollments();
                    this.loadDashboard();
                } catch (error) {
                    this.showToast(error.message, 'error');
                }
            }
        });
    },

    // --- Attendance Module ---
    async loadAttendance() {
        const courseId = document.getElementById('attendance-filter-course')?.value;
        const dateVal = document.getElementById('attendance-filter-date')?.value;

        try {
            const records = await API.getAttendance({
                course_id: courseId || null,
                date: dateVal || null
            });
            this.renderAttendanceTable(records);
        } catch (error) {
            this.showToast('Failed to load attendance logs: ' + error.message, 'error');
        }
    },

    renderAttendanceTable(records) {
        const tbody = document.getElementById('attendance-table-tbody');
        if (!tbody) return;

        if (records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-gray-500">No attendance logs found.</td></tr>`;
            return;
        }

        tbody.innerHTML = records.map(r => `
            <tr class="hover:bg-slate-50 border-b border-gray-100 transition">
                <td class="py-3 px-4 font-medium text-gray-900">${r.date}</td>
                <td class="py-3 px-4">
                    <div class="font-medium text-gray-900">${this.escape(r.student_name)}</div>
                    <div class="text-xs text-indigo-600 font-mono">${this.escape(r.student_roll)}</div>
                </td>
                <td class="py-3 px-4">
                    <span class="font-medium text-gray-800">${this.escape(r.course_code)}</span> - ${this.escape(r.course_name)}
                </td>
                <td class="py-3 px-4">${this.renderAttendanceBadge(r.status)}</td>
                <td class="py-3 px-4 text-sm text-gray-500">${this.escape(r.remarks || '-')}</td>
                <td class="py-3 px-4 text-right">
                    <button onclick="App.deleteAttendanceRecord(${r.id})" class="p-1.5 text-gray-400 hover:text-red-600 transition"><i class="fas fa-trash-alt"></i></button>
                </td>
            </tr>
        `).join('');
    },

    async openMarkAttendanceModal() {
        const form = document.getElementById('attendance-form');
        form.reset();
        document.getElementById('attendance-form-date').value = new Date().toISOString().split('T')[0];
        
        // Populate Course dropdown
        const courseSelect = document.getElementById('attendance-form-course');
        courseSelect.innerHTML = '<option value="">Select Course</option>' + this.courses.map(c => `
            <option value="${c.id}">${this.escape(c.code)} - ${this.escape(c.name)}</option>
        `).join('');

        // Student dropdown is locked until a course is chosen
        const studentSelect = document.getElementById('attendance-form-student');
        studentSelect.innerHTML = '<option value="">-- Please select a course first --</option>';
        studentSelect.disabled = true;

        const countBadge = document.getElementById('attendance-form-enrolled-count');
        if (countBadge) countBadge.textContent = '';
        const warningEl = document.getElementById('attendance-form-warning');
        if (warningEl) warningEl.classList.add('hidden');

        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = false;

        this.openModal('attendance-modal');
    },

    async onAttendanceCourseChange(courseId) {
        const studentSelect = document.getElementById('attendance-form-student');
        const countBadge = document.getElementById('attendance-form-enrolled-count');
        const warningEl = document.getElementById('attendance-form-warning');
        const submitBtn = document.querySelector('#attendance-form button[type="submit"]');
        if (!studentSelect) return;

        if (!courseId) {
            studentSelect.innerHTML = '<option value="">-- Please select a course first --</option>';
            studentSelect.disabled = true;
            if (countBadge) countBadge.textContent = '';
            if (warningEl) warningEl.classList.add('hidden');
            if (submitBtn) submitBtn.disabled = false;
            return;
        }

        studentSelect.disabled = true;
        studentSelect.innerHTML = '<option value="">Loading enrolled students...</option>';

        try {
            const enrolledStudents = await API.getCourseEnrolledStudents(courseId);
            if (!enrolledStudents || enrolledStudents.length === 0) {
                studentSelect.innerHTML = '<option value="">No students enrolled in this course</option>';
                studentSelect.disabled = true;
                if (countBadge) countBadge.textContent = '0 Enrolled';
                if (warningEl) {
                    warningEl.textContent = '⚠️ There are no active students enrolled in this course yet. Please enroll students first.';
                    warningEl.classList.remove('hidden');
                }
                if (submitBtn) submitBtn.disabled = true;
            } else {
                studentSelect.innerHTML = '<option value="">Select Enrolled Student (' + enrolledStudents.length + ' enrolled)</option>' + enrolledStudents.map(s => `
                    <option value="${s.id}">${this.escape(s.roll_number)} - ${this.escape(s.full_name)} (${this.escape(s.department_code || 'Dept')})</option>
                `).join('');
                studentSelect.disabled = false;
                if (countBadge) countBadge.textContent = `${enrolledStudents.length} Enrolled`;
                if (warningEl) warningEl.classList.add('hidden');
                if (submitBtn) submitBtn.disabled = false;
            }
        } catch (error) {
            studentSelect.innerHTML = '<option value="">Failed to load enrolled students</option>';
            studentSelect.disabled = true;
            console.error('Error fetching enrolled students:', error);
        }
    },

    async handleAttendanceFormSubmit(e) {
        e.preventDefault();
        const data = {
            student_id: parseInt(document.getElementById('attendance-form-student').value),
            course_id: parseInt(document.getElementById('attendance-form-course').value),
            date: document.getElementById('attendance-form-date').value,
            status: document.getElementById('attendance-form-status').value,
            remarks: document.getElementById('attendance-form-remarks').value.trim() || null
        };

        try {
            await API.markAttendance(data);
            this.showToast('Attendance recorded!', 'success');
            this.closeModal('attendance-modal');
            this.loadAttendance();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    async deleteAttendanceRecord(id) {
        try {
            await API.deleteAttendance(id);
            this.showToast('Attendance entry deleted', 'success');
            this.loadAttendance();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    },

    // --- Settings / Database Status ---
    async loadSystemStatus() {
        try {
            const status = await API.getSystemStatus();
            const badge = document.getElementById('db-status-badge');
            if (badge) {
                if (status.engine === 'mysql') {
                    badge.innerHTML = `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800"><span class="w-2 h-2 mr-1.5 bg-emerald-500 rounded-full animate-pulse"></span>MySQL: ${status.database}</span>`;
                } else {
                    badge.innerHTML = `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800" title="${status.message}"><span class="w-2 h-2 mr-1.5 bg-amber-500 rounded-full"></span>SQLite (Fallback)</span>`;
                }
            }
        } catch (error) {
            console.error('System status query failed:', error);
        }
    },

    async loadSettings() {
        try {
            const engEl = document.getElementById('settings-engine');
            if (!engEl) return;
            const status = await API.getSystemStatus();
            engEl.textContent = status.engine.toUpperCase();
            const hostEl = document.getElementById('settings-host');
            if (hostEl) hostEl.textContent = status.host;
            const portEl = document.getElementById('settings-port');
            if (portEl) portEl.textContent = status.port;
            const dbEl = document.getElementById('settings-db');
            if (dbEl) dbEl.textContent = status.database;
            const msgEl = document.getElementById('settings-status-msg');
            if (msgEl) msgEl.textContent = status.message;
            
            const badge = document.getElementById('settings-status-badge');
            if (badge) {
                badge.className = status.engine === 'mysql' ? 'px-3 py-1 text-sm font-semibold rounded-full bg-emerald-100 text-emerald-800' : 'px-3 py-1 text-sm font-semibold rounded-full bg-amber-100 text-amber-800';
                badge.textContent = status.engine === 'mysql' ? 'Connected to MySQL' : 'Running SQLite Mode';
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    },

    // --- Modals & Toasts Helpers ---
    openModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.remove('hidden');
    },

    closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.add('hidden');
    },

    openConfirmModal({ title, message, confirmText, confirmClass, onConfirm }) {
        document.getElementById('confirm-modal-title').textContent = title || 'Confirm Action';
        document.getElementById('confirm-modal-body').innerHTML = message || 'Are you sure?';
        const confirmBtn = document.getElementById('confirm-modal-btn');
        confirmBtn.textContent = confirmText || 'Confirm';
        confirmBtn.className = `px-4 py-2 text-sm font-semibold text-white rounded-lg transition ${confirmClass || 'bg-indigo-600 hover:bg-indigo-700'}`;
        
        // Single fire listener
        const newBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);
        newBtn.addEventListener('click', () => {
            this.closeModal('confirm-modal');
            if (onConfirm) onConfirm();
        });

        this.openModal('confirm-modal');
    },

    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast-item flex items-center p-4 mb-3 rounded-xl shadow-lg border max-w-sm text-sm transition-all duration-300 ${
            type === 'success' ? 'bg-white border-emerald-200 text-emerald-800' :
            type === 'error' ? 'bg-white border-rose-200 text-rose-800' :
            'bg-white border-blue-200 text-blue-800'
        }`;

        const icon = type === 'success' ? 'fa-check-circle text-emerald-500' :
                     type === 'error' ? 'fa-exclamation-circle text-rose-500' :
                     'fa-info-circle text-blue-500';

        toast.innerHTML = `
            <i class="fas ${icon} text-lg mr-3"></i>
            <div class="flex-1 font-medium">${this.escape(message)}</div>
            <button class="ml-2 text-gray-400 hover:text-gray-700"><i class="fas fa-times"></i></button>
        `;

        toast.querySelector('button').addEventListener('click', () => toast.remove());
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },

    // --- Badge Renderers ---
    renderStatusBadge(status) {
        const map = {
            'Active': 'badge-active',
            'Graduated': 'badge-graduated',
            'Suspended': 'badge-suspended',
            'Inactive': 'badge-inactive'
        };
        const cls = map[status] || 'bg-gray-100 text-gray-800';
        return `<span class="px-2.5 py-0.5 rounded-full text-xs font-semibold ${cls}">${status}</span>`;
    },

    renderAttendanceBadge(status) {
        const map = {
            'Present': 'badge-present',
            'Absent': 'badge-absent',
            'Late': 'badge-late',
            'Excused': 'badge-excused'
        };
        const cls = map[status] || 'bg-gray-100 text-gray-800';
        return `<span class="px-2 py-0.5 rounded-full text-xs font-semibold ${cls}">${status}</span>`;
    },

    escape(str) {
        if (str === null || str === undefined) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },

    // --- Event Listeners Attachment ---
    setupEventListeners() {
        // Modal Backdrop & Close button clicks
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal || e.target.closest('[data-modal-close]')) {
                    modal.classList.add('hidden');
                }
            });
        });

        // ESC key closes modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
            }
        });

        // Form submissions
        document.getElementById('student-form')?.addEventListener('submit', (e) => this.handleStudentFormSubmit(e));
        document.getElementById('course-form')?.addEventListener('submit', (e) => this.handleCourseFormSubmit(e));
        document.getElementById('dept-form')?.addEventListener('submit', (e) => this.handleDeptFormSubmit(e));
        document.getElementById('enrollment-form')?.addEventListener('submit', (e) => this.handleEnrollmentFormSubmit(e));
        document.getElementById('grade-form')?.addEventListener('submit', (e) => this.handleGradeFormSubmit(e));
        document.getElementById('attendance-form')?.addEventListener('submit', (e) => this.handleAttendanceFormSubmit(e));

        // Filters in Courses & Attendance
        document.getElementById('course-filter-dept')?.addEventListener('change', () => this.loadCourses());
        document.getElementById('attendance-filter-course')?.addEventListener('change', () => this.loadAttendance());
        document.getElementById('attendance-filter-date')?.addEventListener('change', () => this.loadAttendance());

        // Dynamic cascading dropdowns for Enrollment and Attendance
        document.getElementById('enrollment-form-student')?.addEventListener('change', (e) => this.onEnrollStudentChange(e.target.value));
        document.getElementById('attendance-form-course')?.addEventListener('change', (e) => this.onAttendanceCourseChange(e.target.value));
    }
};

