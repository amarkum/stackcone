"""Extra teaching material for the Git & CLI lessons."""

EXTRA = {}

EXTRA["git-command-line"] = {
    "intro": [
        ("h2", "Why learn the terminal at all?"),
        ("p", "Every graphical app you use is a friendly layer on top of commands. The terminal is the plain, direct way to talk to your computer: you type a short instruction, press Enter and it answers. It looks intimidating for a day and then becomes the fastest tool you own. Nearly every developer tool (Git, Docker, Python, Node, cloud services) is driven from it, and it is the same on servers where there is no mouse at all."),
        ("p", "One rule makes it less scary: <strong>a command is a verb plus optional details</strong>. <code>ls</code> lists, <code>cd</code> changes folder, <code>mkdir</code> makes a folder. Add a flag such as <code>-l</code> for options and a path for the target."),
    ],
    "more": [
        ("h2", "Anatomy of a command"),
        ("code", "bash", "ls -la ~/projects\n#  |  |    |\n#  |  |    +-- argument: what to act on\n#  |  +------- flags: change how it behaves (-l long list, -a include hidden)\n#  +---------- command: what to do"),
        ("h2", "A first session, step by step"),
        ("p", "Type these one at a time and read what each prints. <code>$</code> is the prompt, not part of the command."),
        ("code", "bash", "$ pwd                    # where am I?\n/Users/ada\n$ mkdir practice         # make a folder\n$ cd practice            # go into it\n$ echo \"hello\" > a.txt   # create a file containing hello\n$ ls\na.txt\n$ cat a.txt              # show its contents\nhello\n$ cd ..                  # go back up one level"),
        ("h2", "Paths: absolute and relative"),
        ("ul", [
            "<strong>Absolute</strong> paths start at the root: <code>/Users/ada/practice/a.txt</code>. They work from anywhere.",
            "<strong>Relative</strong> paths start from where you are: <code>practice/a.txt</code>. <code>.</code> means here, <code>..</code> means the parent folder, and <code>~</code> means your home folder.",
        ]),
        ("h2", "Keyboard shortcuts that save hours"),
        ("ul", [
            "<strong>Tab</strong> completes file and folder names. Press it constantly; it prevents typos.",
            "<strong>Up arrow</strong> brings back previous commands; <strong>Ctrl+R</strong> searches your history.",
            "<strong>Ctrl+C</strong> stops a running command; <strong>Ctrl+L</strong> clears the screen.",
            "<code>man ls</code> or <code>ls --help</code> shows the manual for any command.",
        ]),
        ("note", "Be careful with rm", "<code>rm</code> deletes permanently; there is no recycle bin. <code>rm -rf folder</code> removes a folder and everything in it without asking. Read the command twice before pressing Enter, and never run one you copied without understanding it."),
    ],
    "recap": [
        "A command is a verb, optional flags and arguments: <code>ls -la folder</code>.",
        "<code>pwd</code>, <code>ls</code>, <code>cd</code>, <code>mkdir</code>, <code>cat</code> are the survival kit.",
        "Use Tab to complete, the Up arrow for history and <code>--help</code> when stuck.",
        "<code>rm</code> is permanent; double-check before deleting.",
    ],
}

EXTRA["git-introduction"] = {
    "intro": [
        ("h2", "The problem Git solves"),
        ("p", "You have probably saved files called <code>report_final.docx</code>, <code>report_final2.docx</code> and <code>report_REALLY_final.docx</code>. Now imagine ten people editing the same project. Git is a system that remembers every version of every file, who changed what and why, and lets you go back to any point. Instead of copies of files, you keep <strong>one folder plus a complete history</strong>."),
        ("p", "Git is also what makes teamwork possible. Everyone works on their own copy, and Git combines the changes. It is the industry standard, used by essentially every software team and hosted by services such as GitHub and GitLab."),
    ],
    "more": [
        ("h2", "Think of commits as save points in a game"),
        ("p", "A <strong>commit</strong> is a snapshot of your project at one moment, with a message explaining it. You can always return to an earlier save point. A history is simply a chain of these snapshots, each pointing at the one before it."),
        ("code", "bash", "commit 3  \"Add contact form\"      <- you are here\n   |\ncommit 2  \"Style the header\"\n   |\ncommit 1  \"Create homepage\""),
        ("h2", "A complete first walkthrough"),
        ("p", "Follow along in an empty folder. Each command is explained so nothing is magic."),
        ("code", "bash", "$ mkdir my-site && cd my-site\n$ git init                       # start tracking this folder\nInitialized empty Git repository in .../my-site/.git/\n\n$ echo \"<h1>Hello</h1>\" > index.html\n$ git status                     # what has changed?\nUntracked files:\n        index.html\n\n$ git add index.html             # stage: choose what goes in the next snapshot\n$ git commit -m \"Create homepage\" # commit: take the snapshot\n[main (root-commit) 3f2a91c] Create homepage\n 1 file changed, 1 insertion(+)\n\n$ git log --oneline              # view the history\n3f2a91c Create homepage"),
        ("h2", "Why is there a staging area?"),
        ("p", "You may have edited five files but only want two of them in this commit because they belong to one idea. <code>git add</code> lets you pick exactly what goes into the snapshot. It feels like an extra step at first; later it is what keeps your history clean and understandable."),
        ("h2", "The three states of a file"),
        ("ul", [
            "<strong>Modified</strong>: you changed it, but Git has not been told to include it yet.",
            "<strong>Staged</strong>: you ran <code>git add</code>; it will be in the next commit.",
            "<strong>Committed</strong>: it is safely stored in the history.",
        ]),
        ("p", "<code>git status</code> tells you which state each file is in. When you are lost, run it. It is the most useful Git command and also suggests what to do next."),
        ("h2", "Seeing what changed"),
        ("code", "bash", "$ echo \"<p>Welcome</p>\" >> index.html\n$ git diff                       # changes not yet staged\n+<p>Welcome</p>\n\n$ git add index.html\n$ git diff --staged              # changes that will be committed"),
    ],
    "recap": [
        "Git keeps a complete history of your project as a chain of commits (snapshots).",
        "The everyday loop: edit, <code>git add</code>, <code>git commit -m</code>.",
        "<code>git status</code>, <code>git diff</code> and <code>git log --oneline</code> tell you where you are.",
        "Write commit messages that explain <em>why</em>; your future self will thank you.",
    ],
}

EXTRA["git-branching-merging"] = {
    "intro": [
        ("h2", "Branches let you experiment safely"),
        ("p", "Imagine you want to try a risky redesign but the site must keep working for visitors. A <strong>branch</strong> is a separate line of development: you copy the current state, work on your copy, and if it goes well you merge it back. If it goes badly you delete the branch and nothing was harmed. Branches are cheap in Git (just a pointer), so professional teams create one for every feature and bug fix."),
        ("code", "bash", "main:     A---B---C\n               \\\nfeature:        D---E     <- your experiment, isolated from main"),
    ],
    "more": [
        ("h2", "A full feature workflow"),
        ("code", "bash", "$ git switch -c add-search        # create a branch and move to it\nSwitched to a new branch 'add-search'\n\n$ # ...edit files...\n$ git add .\n$ git commit -m \"Add search box\"\n\n$ git switch main               # go back to main\n$ git merge add-search          # bring the feature in\nUpdating 3f2a91c..9d1e4b7\nFast-forward\n search.html | 12 ++++++++++++\n\n$ git branch -d add-search      # tidy up, the work is now on main"),
        ("h2", "Fast-forward versus merge commit"),
        ("p", "If <code>main</code> has not moved since you branched, Git simply slides the pointer forward: a <strong>fast-forward</strong>, no extra commit. If <code>main</code> also gained new commits, Git creates a <strong>merge commit</strong> that joins the two lines and has two parents."),
        ("h2", "Conflicts are normal, not a disaster"),
        ("p", "A conflict happens only when two branches change the <em>same lines</em> of the same file, and Git cannot decide which to keep. It stops and marks the file. Your job is to choose, then finish the merge."),
        ("code", "text", "<<<<<<< HEAD\n<h1>Welcome to our shop</h1>\n=======\n<h1>Welcome to the store</h1>\n>>>>>>> add-search"),
        ("ul", [
            "Everything between <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code> and <code>=======</code> is what is on your current branch.",
            "Everything between <code>=======</code> and <code>&gt;&gt;&gt;&gt;&gt;&gt;&gt;</code> is what the other branch has.",
            "Edit the file to the version you want, deleting all three marker lines.",
            "Then <code>git add file</code> and <code>git commit</code> to complete the merge.",
        ]),
        ("note", "Stuck mid-merge?", "<code>git merge --abort</code> returns to the state before you started, so it is always safe to try again."),
    ],
    "recap": [
        "A branch is an isolated line of work; create one per feature or fix.",
        "<code>git switch -c name</code> creates and enters a branch; <code>git merge name</code> combines it.",
        "Conflicts only occur when the same lines changed; you resolve them by editing and committing.",
        "<code>git merge --abort</code> cancels a merge you are not ready to finish.",
    ],
}

EXTRA["git-remote-github"] = {
    "intro": [
        ("h2", "Your computer is not the only copy"),
        ("p", "So far your history lives only on your laptop. A <strong>remote</strong> is another copy of the repository hosted elsewhere, usually on GitHub. It is your backup, the place teammates fetch your work from, and the home of code review. The whole collaboration model is just two motions: <strong>push</strong> your commits up and <strong>pull</strong> theirs down."),
        ("code", "bash", "your laptop  --git push-->  GitHub (origin)  <--git push--  teammate\nyour laptop  <--git pull--  GitHub (origin)  --git pull-->  teammate"),
    ],
    "more": [
        ("h2", "Publishing a project to GitHub, step by step"),
        ("ul", [
            "Create an empty repository on GitHub and copy its URL.",
            "Connect your local project to it and give the connection the conventional name <code>origin</code>.",
            "Push your branch, and set it up to track so later pushes are just <code>git push</code>.",
        ]),
        ("code", "bash", "$ git remote add origin git@github.com:ada/my-site.git\n$ git remote -v\norigin  git@github.com:ada/my-site.git (fetch)\norigin  git@github.com:ada/my-site.git (push)\n\n$ git push -u origin main\nEnumerating objects: 3, done.\nTo github.com:ada/my-site.git\n * [new branch]      main -> main\nbranch 'main' set up to track 'origin/main'."),
        ("h2", "Getting a copy of someone else's project"),
        ("code", "bash", "$ git clone https://github.com/ada/my-site.git\nCloning into 'my-site'...\n$ cd my-site\n$ git log --oneline   # the full history came with it"),
        ("h2", "The pull request workflow, in plain steps"),
        ("ul", [
            "<strong>Branch</strong>: <code>git switch -c fix-typo</code>.",
            "<strong>Commit</strong> your change and <strong>push</strong> the branch: <code>git push -u origin fix-typo</code>.",
            "<strong>Open a pull request</strong> on GitHub: a page where teammates review, comment on and discuss your changes.",
            "<strong>Update</strong> it by pushing more commits to the same branch if reviewers ask for changes.",
            "<strong>Merge</strong> the pull request once approved, then delete the branch and <code>git pull</code> on <code>main</code>.",
        ]),
        ("h2", "fetch versus pull"),
        ("p", "<code>git fetch</code> downloads new commits but does not touch your files, so you can look first (<code>git log origin/main</code>). <code>git pull</code> is fetch plus merge in one step. When in doubt, fetch first; it is always safe."),
        ("note", "Rejected push?", "A message like <code>rejected: non-fast-forward</code> just means the remote has commits you do not. Run <code>git pull</code>, resolve any conflict, and push again. Avoid <code>--force</code> on shared branches."),
    ],
    "recap": [
        "A remote (usually <code>origin</code> on GitHub) is a shared copy of your repository.",
        "<code>git push</code> sends your commits; <code>git pull</code> brings others' commits down.",
        "<code>git clone</code> copies a whole repository with its history.",
        "Pull requests are branches proposed for review before merging.",
    ],
}

EXTRA["git-undo-workflows"] = {
    "intro": [
        ("h2", "Mistakes are cheap in Git"),
        ("p", "The reason experienced developers are relaxed about Git is that almost everything can be undone, as long as it was committed. The trick is choosing the right undo for the situation. Ask two questions: <strong>Has it been committed?</strong> and <strong>Has it been pushed and shared?</strong> The answers pick the tool."),
        ("ul", [
            "Not committed yet → <code>git restore</code> (throws away edits).",
            "Committed, not pushed → <code>git commit --amend</code> or <code>git reset</code> (rewrites your own history).",
            "Already pushed and shared → <code>git revert</code> (adds a new commit that cancels the old one; never rewrites shared history).",
        ]),
    ],
    "more": [
        ("h2", "Situation 1: I edited a file and want the old version back"),
        ("code", "bash", "$ git status\n  modified:   index.html\n$ git restore index.html          # discards the edits (cannot be undone!)\n$ git status\nnothing to commit, working tree clean"),
        ("h2", "Situation 2: I committed too early or with a typo in the message"),
        ("code", "bash", "$ git commit -m \"Add serch box\"\n$ git commit --amend -m \"Add search box\"   # fixes the last commit message\n\n$ git add forgotten-file.css\n$ git commit --amend --no-edit               # adds the file to the last commit"),
        ("h2", "Situation 3: a bad commit is already on GitHub"),
        ("code", "bash", "$ git log --oneline\n9d1e4b7 Break the login page\n3f2a91c Create homepage\n\n$ git revert 9d1e4b7        # creates a new commit that undoes it\n[main c07be21] Revert \"Break the login page\""),
        ("p", "Because <code>revert</code> only adds history, teammates who already pulled the bad commit are not affected, and the story stays honest."),
        ("h2", "Situation 4: I need to switch tasks but my work is half done"),
        ("code", "bash", "$ git stash                 # sets your edits aside, working tree is clean\n$ git switch hotfix         # fix something urgent...\n$ git switch main\n$ git stash pop             # bring your unfinished work back"),
        ("h2", "Situation 5: \"I lost a commit!\""),
        ("p", "Git keeps a private diary of everywhere your branch has pointed, called the <strong>reflog</strong>. Even after a bad reset the commit is usually still there for weeks."),
        ("code", "bash", "$ git reflog\nc07be21 HEAD@{0}: revert: Revert \"Break the login page\"\n9d1e4b7 HEAD@{1}: commit: Break the login page\n3f2a91c HEAD@{2}: commit (initial): Create homepage\n\n$ git reset --hard 3f2a91c   # jump back to any of those points"),
        ("note", "reset --hard is the sharp knife", "<code>git reset --hard</code> and <code>git restore</code> discard uncommitted work permanently. Commit or stash first if you are not sure."),
    ],
    "recap": [
        "Pick the undo by asking: committed? pushed?",
        "<code>restore</code> for edits, <code>amend</code>/<code>reset</code> for local commits, <code>revert</code> for shared ones.",
        "<code>stash</code> parks unfinished work; <code>reflog</code> finds \"lost\" commits.",
        "Never rewrite history that others have already pulled.",
    ],
}
